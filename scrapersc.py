import os
import json
import locale
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv

def getAuthCookie():
    load_dotenv()
    session = requests.Session()
    session.get("https://publiek.usc.ru.nl/publiek/login.php")
    session.post(
        "https://publiek.usc.ru.nl/publiek/login.php",
        data={
            "username": os.environ.get("RSC_USERNAME"),
            "password": os.environ.get("RSC_PASSWORD"),
        },
    )
    return session.cookies["publiek"]


def get_rsc_rawsite(sport="fitness", verb=0):
    url = "https://publiek.usc.ru.nl/publiek/laanbod.php?PRESET[Laanbod][inschrijving_id_pool_id][]=768114_2"

    body = {
        "PRESET[Laanbod][inschrijving_id_pool_id][]": "798647_2",
        "PRESET[Laanbod][where_naam_ibp][]": "pack=a%3A5%3A%7Bs%3A6%3A%22n.naam%22%3Bs%3A7%3A%22Fitness%22%3Bs%3A12%3A%22jlap.pool_id%22%3Bs%3A1%3A%222%22%3Bs%3A10%3A%22jlap.intro%22%3Bs%3A0%3A%22%22%3Bs%3A16%3A%22jlap.betaalwijze%22%3Bs%3A6%3A%22gratis%22%3Bs%3A10%3A%22jlap.prijs%22%3Bs%3A4%3A%220.00%22%3B%7D",
    }

    cookies={"publiek": getAuthCookie()}

    response = requests.post(url=url, data=body, cookies=cookies ) #, headers=headers)

    if verb:
        print(response)
    return response.text


def parse_rsc_rawsite(response, verb=0):
    locale.setlocale(locale.LC_TIME, "nl_NL.UTF-8")

    result = BeautifulSoup(response, "lxml") #, "html.parser")

    table = result.find("table", attrs={'class':"responstable clickabletr"})
    
    if verb:
        print('found table: ', table)

    trs = table.find_all("tr")
    if verb:
        print('found {} rows'.format(len(trs)))

    starttimes = []
    nreservations = []
    
    now = datetime.datetime.now()

    for tr in trs:
        cols = tr.find_all('td')
        if len(cols) > 1:
            date = cols[0].text.strip()
            timestart = cols[1].text.strip().split("-")[0] # starting time only
            dateo = datetime.datetime.strptime(date, "%a %d %b %Y")
            tso = datetime.datetime.strptime(timestart, "%H:%M")
            full = datetime.datetime.combine(dateo, tso.time())
            
            nres = cols[3].text.strip().split("/")[0]
            if nres=='VOL':
                nres = 60
            else:
                nres = int(nres)

            starttimes.append(full)
            nreservations.append(nres)

    df = pd.DataFrame({'start': starttimes, 'nres': nreservations, 'now': now})

    return df

def save_df(df, fileroot='data/', verb=0):
    time = datetime.datetime.now().strftime('%Y%m%d%H%M')
    filename = fileroot + time + '.csv'
    df.to_csv(filename, index=False)
    if verb:
        print('saved to ', filename)

def main(verb=0):
    responsetext = get_rsc_rawsite(verb=verb)
    df = parse_rsc_rawsite(responsetext, verb=verb)
    save_df(df, verb=verb)

if __name__ == "__main__":
    main()
