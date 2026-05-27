variable "aws_region" {
  default = "us-west-2"
}

variable "glue_job_name" {
  default = "gitlab-glue-job"
}

variable "s3_bucket" {
  default = "dev-cog-generic-glue-scripts"
}

variable "glue_role_arn" {

  description = "Glue IAM Role ARN"

  type = string
}
