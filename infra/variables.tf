variable "aws_region" {
  default = "us-west-2"
}

variable "lambda_function_name" {
  default = "gitlab-lambda"
}

variable "glue_job_name" {
  default = "gitlab-glue-job"
}

variable "s3_bucket" {
  default = "dev-cog-generic-glue-scripts"
}

variable "lambda_role_arn" {

  description = "Lambda IAM Role ARN"

  type = string
}

variable "glue_role_arn" {

  description = "Glue IAM Role ARN"

  type = string
}
