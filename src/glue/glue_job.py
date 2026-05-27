import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import json
import pandas as pd
import numpy as np
import boto3
import math
import datetime
import time
from datetime import timedelta
from boto3.dynamodb.conditions import Key, Attr

d = datetime.datetime.now()
print(d)

client_lambda = boto3.client('lambda', region_name='us-west-2')

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
athena_client = boto3.client("athena", region_name = "us-west-2")
dynamo_table = dynamodb.Table('cmp-jobs-tracker-v3')
s3_resource = boto3.resource('s3')

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'client_name','processing_date'])
client_name = args['client_name']
processing_date = args['processing_date']

# args = getResolvedOptions(sys.argv, ['JOB_NAME'])
# client_name = 'vivachicken'
# processing_date = '2022-09-18'  
print('args ', args)
print(client_name)

env = "prod"
bucket = env + '-cog-' + client_name
s3_bucket = s3_resource.Bucket(bucket)
bucket_level = 's3://{bucket}/'.format(bucket=bucket)
cust_analytic_file = 'data/stage/global_control_flag/cust_analytic_pre_gcf/'

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

class QueryIncompleteException(Exception):
    pass

def write_cust_analytic_cust_random_num():

    print("function invoked")

    cust_analytic_file_list = []
    for obj in s3_bucket.objects.filter(Prefix=cust_analytic_file):
        cust_analytic_file_list.append(bucket_level + obj.key)
    
    print("before_reading")
    cust_analytic_df_temp = [pd.read_parquet(path) for path in cust_analytic_file_list]
    print("after_reading")
    
    try: 
        cust_analytic_df = pd.concat(cust_analytic_df_temp)
    except Exception as e :
        print ("error : ", e)
        return {'client_name': client_name}
        
    print("after_concatination") 
    cust_analytic_df['distance_bucket'] = np.select(
        [cust_analytic_df['distance_close'].between(0, 5, inclusive=True),
         cust_analytic_df['distance_close'].between(6, 10, inclusive=True),
         cust_analytic_df['distance_close'].isnull()
        ],
        [
        1,
        2,
        4
        ],
        default=3)

    print("ca_df len :", len(cust_analytic_df))
    
    # _temp_for_tval = cust_analytic_df[['cust_id','geo_id_fav', 'dim_value', 'distance_bucket']] # Commented by RAMU on 2022-09-15
    _temp_for_tval = cust_analytic_df[['cust_id','geo_id_fav','dim_lifecycle','dim_value', 'distance_bucket']] # RAMU added dim_lifecycle to prevent from getting errored on 2022-09-15
    
    
    _temp_for_tval['_drop_this_rand1'] = np.random.uniform(0,1,len(_temp_for_tval))
    
    # _temp_for_tval.sort_values(by = ['geo_id_fav', 'dim_value', 'distance_bucket','_drop_this_rand1'], inplace = True)
    _temp_for_tval.sort_values(by = ['geo_id_fav', 'dim_lifecycle', 'distance_bucket','_drop_this_rand1'], inplace = True) # commented temporarily 
    # _temp_for_tval.sort_values(by = ['dim_value', 'dim_lifecycle', 'distance_bucket','_drop_this_rand1'], inplace = True, ascending=[False, True, True, True]) # this line is for testing 

    _temp_for_tval['_tval_counter'] = 0
    _temp_for_tval['_tval_group'] = 1
    
    _temp_for_tval['row_number'] = np.arange(len(_temp_for_tval))
    
    _temp_for_tval['_tval_group'] = _temp_for_tval['row_number'].apply(lambda x:math.ceil(x/100))
    
    _temp_for_tval['cust_random_num_1'] = _temp_for_tval.groupby(['_tval_group']).cumcount()+1
    
    histdt_f = cust_analytic_df.merge(_temp_for_tval[['cust_id','cust_random_num_1']].drop_duplicates(), on = ['cust_id'],how = 'left')
    
    histdt_f.to_parquet('s3://{env}-cog-{client_name}/data/stage/global_control_flag/cust_analytic_post_gcf/data.parquet'.format(client_name = client_name, env = env), index=False)
    return {'client_name': client_name}

try: 
    write_cust_analytic_cust_random_num()

    # client_lambda.invoke(
    #     FunctionName = 'prod-cog-global-control-flag',
    #     InvocationType = 'Event',
    #     LogType = 'None',
    #     Payload = json.dumps({'client_name': client_name, 'processing_date' : processing_date, 'stage': 'post_global_control_glue_job'})
    # )

except Exception as e: 
    dynamo_table.update_item( 
        Key = {"client_id": client_name},         
        UpdateExpression='SET gcf_status = :val1 ', 
        ExpressionAttributeValues={':val1': "Failed"}) 
    print(e) 
    raise e

job.commit()