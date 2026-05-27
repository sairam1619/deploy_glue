#!/bin/bash
set -e

aws s3 cp src/glue/glue_job.py s3://dev-cog-generic-glue-scripts/new/

echo "Glue script uploaded successfully"
