import pandas as pd
import json

def load(**context):
    transformed_data_fpath = context['ti'].xcom_pull(task_ids='transform_task')
    print(transformed_data_fpath)
    tdf = pd.read_json(transformed_data_fpath)
    print(tdf.head())
    print('rat')