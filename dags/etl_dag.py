from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable


# load secrets, should switch to adding them
# to Airflow Variables perhaps with a bash script instead.
from dotenv import load_dotenv

from etl.extract import extract
from etl.transform import transform
from etl.load import load
from etl.clean import clean_up

dargs = {
    'owner' : 'dmtr',
    'start_date': "2025-03-01",
    'catchup': False,
}

with DAG(dag_id = "etl_dag", default_args=dargs):
    
    extract = PythonOperator(
        task_id = "extract_task",
        python_callable = extract,
        provide_context = True
    )

    transform = PythonOperator(
        task_id = "transform_task",
        python_callable = transform,
        provide_context = True
    )

    load = PythonOperator(
        task_id = "load_task",
        python_callable = load,
        provide_context = True
    )

    clean = PythonOperator(
        task_id = "clean_task",
        python_callable = clean_up,
        provide_context = True
    )

    extract >> transform >> load >> clean