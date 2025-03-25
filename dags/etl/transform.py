import datetime
import locale
import json
import os

from airflow.models import Variable

TRANSFORM_DIR = Variable.get("TRANSFORM_DIR", default_var="/tmp/etl_dag/transform/")

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
    
def parse_rsc_page(page):
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

    data = {'starttimes': [str(st) for st in starttimes], 'nreservations': nreservations}
    return data

def read_extracted_rawpage(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        rawpage = f.read()
    return rawpage

def write_transformed_data(data):
    os.makedirs(TRANSFORM_DIR, exist_ok=True)
    file_path = os.path.join(TRANSFORM_DIR, 'latest_data.json')

    with open(file_path, 'w') as f:
        json.dump(data, f)
    print('transform wrote data to data.json')

    return file_path

def transform(**context):

    rawpage_fpath = context['ti'].xcom_pull(task_ids='extract_task')
    rawpage = read_extracted_rawpage(rawpage_fpath)
    transformed_data = parse_rsc_page(rawpage)
    transformed_data_fpath = write_transformed_data(transformed_data)
    
    return transformed_data_fpath