#################################################
# PACKAGE LAMBDA
#################################################

data "archive_file" "lambda_zip" {

  type = "zip"

  source_dir = "../src/lambda_code"

  output_path = "../src/lambda_code/lambda.zip"
}

#################################################
# LAMBDA FUNCTION
#################################################

resource "aws_lambda_function" "lambda_function" {

  function_name = var.lambda_function_name

  role = var.lambda_role_arn

  handler = "app.lambda_handler"

  runtime = "python3.14"

  filename = data.archive_file.lambda_zip.output_path

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}