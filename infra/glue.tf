resource "aws_glue_job" "glue_job" {

  name = var.glue_job_name

  role_arn = var.glue_role_arn

  command {

    name = "glueetl"

    script_location = "s3://${var.s3_bucket}/new/glue_job.py"

    python_version = "3"
  }

  glue_version = "4.0"

  max_capacity = 2
}