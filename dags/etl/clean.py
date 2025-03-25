import os
from airflow.models import Variable

def clean_up(**context):

    extract_data = context['ti'].xcom_pull(task_ids='extract_task')
    transform_data = context['ti'].xcom_pull(task_ids='transform_task')

    # delete the files
    print('cleaning up')
    print('extract_data:', extract_data)
    print('transform_data:', transform_data)
    os.remove(extract_data)
    os.remove(transform_data)