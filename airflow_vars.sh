#!/bin/bash

set -a
source .env
set +a

echo "Passing secrets to Airflow variables"


airflow variables set RSC_USERNAME "$RSC_USERNAME"
airflow variables set RSC_PASSWORD "$RSC_PASSWORD"

airflow variables set EXTRACT_DIR "$EXTRACT_DIR"
airflow variables set TRANSFORM_DIR "$TRANSFORM_DIR"
airflow variables set LOAD_DIR "$LOAD_DIR"

echo "All Airflow varaibles set succesfully!"