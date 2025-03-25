from airflow.models import Variable
import requests
import os

RSC_USERNAME = Variable.get("RSC_USERNAME")
RSC_PASSWORD = Variable.get("RSC_PASSWORD")
EXTRACT_DIR = Variable.get("EXTRACT_DIR", default_var="/tmp/etl_dag/extract/")


def getAuthCookie():
    session = requests.Session()
    res = session.get("https://publiek.usc.ru.nl/publiek/login.php")
    if res.status_code != 200:
        raise Exception("Failed to get login page, check internet connection!")
    res = session.post(
        "https://publiek.usc.ru.nl/publiek/login.php",
        data={
            "username": RSC_USERNAME,
            "password": RSC_PASSWORD,
        },
    )
    if res.status_code != 200:
        raise Exception("Failed to login, check credentials!")
    
    return session.cookies["publiek"]

def get_rsc_rawsite(login_cookie):
    url = "https://publiek.usc.ru.nl/publiek/laanbod.php?PRESET[Laanbod][inschrijving_id_pool_id][]=768114_2"

    body = {
        "PRESET[Laanbod][inschrijving_id_pool_id][]": "859942_2",
        "PRESET[Laanbod][where_naam_ibp][]": "pack=a%3A5%3A%7Bs%3A6%3A%22n.naam%22%3Bs%3A7%3A%22Fitness%22%3Bs%3A12%3A%22jlap.pool_id%22%3Bs%3A1%3A%222%22%3Bs%3A10%3A%22jlap.intro%22%3Bs%3A0%3A%22%22%3Bs%3A16%3A%22jlap.betaalwijze%22%3Bs%3A6%3A%22gratis%22%3Bs%3A10%3A%22jlap.prijs%22%3Bs%3A4%3A%220.00%22%3B%7D",
    }

    cookies={"publiek": login_cookie}
    res = requests.post(url=url, data=body, cookies=cookies ) #, headers=headers)
    
    if res.status_code != 200:
        raise Exception("Failed to get raw site, check credentials!")
    
    print("Sucessfully fetched raw site!")
    return res

def write_rawsite_to_file(res):
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    file_path = os.path.join(EXTRACT_DIR, 'rawpage.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(res.text)
    
    return file_path

def extract(**context):
    logincookie = getAuthCookie()
    response = get_rsc_rawsite(logincookie)
    file_path = write_rawsite_to_file(response)
    return file_path
