from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime

import pandas as pd
import os
import json
import locale
import datetime
import requests

from git import Repo
from dotenv import load_dotenv

load_dotenv()

dargs = {
    'owner' : 'dmtr',
    'start_date': "2025-03-01",
    'catchup': False,
}

with DAG(dag_id = "etl_dag", default_args=dargs):

    def getAuthCookie():
        session = requests.Session()
        res = session.get("https://publiek.usc.ru.nl/publiek/login.php")
        if res.status_code != 200:
            raise Exception("Failed to get login page, check internet connection!")
        res = session.post(
            "https://publiek.usc.ru.nl/publiek/login.php",
            data={
                "username": os.environ.get("RSC_USERNAME"),
                "password": os.environ.get("RSC_PASSWORD"),
            },
        )
        if res.status_code != 200:
            raise Exception("Failed to login, check credentials!")
        return session.cookies["publiek"]

    def get_rsc_rawsite():
        url = "https://publiek.usc.ru.nl/publiek/laanbod.php?PRESET[Laanbod][inschrijving_id_pool_id][]=768114_2"

        body = {
            "PRESET[Laanbod][inschrijving_id_pool_id][]": "859942_2",
            "PRESET[Laanbod][where_naam_ibp][]": "pack=a%3A5%3A%7Bs%3A6%3A%22n.naam%22%3Bs%3A7%3A%22Fitness%22%3Bs%3A12%3A%22jlap.pool_id%22%3Bs%3A1%3A%222%22%3Bs%3A10%3A%22jlap.intro%22%3Bs%3A0%3A%22%22%3Bs%3A16%3A%22jlap.betaalwijze%22%3Bs%3A6%3A%22gratis%22%3Bs%3A10%3A%22jlap.prijs%22%3Bs%3A4%3A%220.00%22%3B%7D",
        }

        cookies={"publiek": getAuthCookie()}
        res = requests.post(url=url, data=body, cookies=cookies )
        
        if res.status_code != 200:
            raise Exception("Failed to get raw site, check credentials!")
        
        print("Sucessfully fetched raw site!")
        Variable.set("rawpage", res.text)

    
    extract = PythonOperator(
        task_id = "extract_task",
        python_callable = get_rsc_rawsite
    )

    def parse_rsc_timeslot(datestr, timestr):
        date = datestr.strip()
        date = date.replace("maa", "mrt")
        timestart = timestr.strip().split("-")[0] # starting time only
        dateo = datetime.datetime.strptime(date, "%a %d %b %Y")
        tso = datetime.datetime.strptime(timestart, "%H:%M")
        full = datetime.datetime.combine(dateo, tso.time())
        return full

    def parse_rsc_res(resstr):
        try:
            if 'VOL' in resstr: # 50 out of 60 spots taken
                return 60
            else:
                nres = resstr.strip().split("/")[0]
                return int(nres)
        except:
            print('Error parsing resstr:', resstr)
            return -1 # error occured
        
    def parse_rsc_page(**kwargs):

        page = Variable.get("rawpage")

        locale.setlocale(locale.LC_TIME, "nl_NL.UTF-8")

        starttimes = []
        nreservations = []

        tablestart = "<table class=\"responstable clickabletr\">"
        tablestartidx = page.find(tablestart) + len(tablestart)
        tableend = "</table>"
        tableendidx = page.find(tableend, tablestartidx) - len(tableend)

        table = page[tablestartidx:tableendidx + len(tableend)]
        trs = table.split("<tr")
        for tr in trs:
            rows = tr.split("<td>")
            if len(rows) > 3: # ensure it's a valid row
                dt = parse_rsc_timeslot(rows[1], rows[2])
                starttimes.append(dt)
                nres = parse_rsc_res(rows[4])
                nreservations.append(nres)

        kwargs['ti'].xcom_push(key='starttimes', value=starttimes)
        kwargs['ti'].xcom_push(key='nreservations', value=nreservations)
        
    
    transform = PythonOperator(
        task_id = "transform_task",
        python_callable = parse_rsc_page,
        provide_context = True
    )

    def store_full_data(**kwargs):
        
        starttimes = kwargs['ti'].xcom_pull(task_ids='transform_task', key='starttimes')
        nreservations = kwargs['ti'].xcom_pull(task_ids='transform_task', key='nreservations')

        print(type(starttimes))
        print(starttimes)

        print(type(nreservations))
        print(nreservations)

        df = pd.DataFrame({
            "starttimes": starttimes,
            "nreservations": nreservations
        })
        print(df)

    load = PythonOperator(
        task_id = "load_task",
        python_callable = store_full_data,
        provide_context = True
    )

    extract >> transform >> load