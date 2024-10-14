import os
import json
import locale
import datetime
import requests
import time

from git import Repo
from dotenv import load_dotenv

def getAuthCookie():
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
        "PRESET[Laanbod][inschrijving_id_pool_id][]": "859942_2",
        "PRESET[Laanbod][where_naam_ibp][]": "pack=a%3A5%3A%7Bs%3A6%3A%22n.naam%22%3Bs%3A7%3A%22Fitness%22%3Bs%3A12%3A%22jlap.pool_id%22%3Bs%3A1%3A%222%22%3Bs%3A10%3A%22jlap.intro%22%3Bs%3A0%3A%22%22%3Bs%3A16%3A%22jlap.betaalwijze%22%3Bs%3A6%3A%22gratis%22%3Bs%3A10%3A%22jlap.prijs%22%3Bs%3A4%3A%220.00%22%3B%7D",
    }
    cookies={"publiek": getAuthCookie()}
    response = requests.post(url=url, data=body, cookies=cookies ) #, headers=headers)
    return response.text

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

    return starttimes, nreservations

def store_full_data(starttimes, nreservations):
    current_time = datetime.datetime.now()

    fulldata = {}
    for i, date in enumerate(starttimes):
        datestr = date.strftime("%Y_%m_%d_%H_%M")
        fulldata[datestr] = nreservations[i]
    
    current_str = current_time.strftime("%Y_%m_%d_%H_%M")
    fpath = os.environ.get('GIT_REPO_PATH')
    fpath = fpath + f"data/{current_str}.json"

    with open(fpath, "w") as f:
        json.dump(fulldata, f)

def plotly_today(starttimes, nreservations):
    today = {}

    current_time = datetime.datetime.now()

    today['updatetime'] = current_time.strftime("%m-%d %H:%M")
    if current_time.hour > 22:
        current_time = current_time + datetime.timedelta(days=1)

    
    todaytime = []
    todayres = []
    for i, date in enumerate(starttimes):
        if date.date() == current_time.date():
            datestr = date.strftime("%H:%M")
            todaytime.append(datestr)
            todayres.append(nreservations[i])
    today['time'] = todaytime
    today['nres'] = todayres
    
    fpath = os.environ.get('GIT_REPO_PATH')
    fpath = fpath +"docs/today.json"
    with open(fpath, "w") as f:
        json.dump(today, f)

def push_to_git():
    try:
        repo = Repo(os.environ.get("GIT_REPO_PATH"))
        repo.git.add("docs/today.json")
        repo.index.commit("New data")
        origin = repo.remote(name="origin")
        origin.push()
    except Exception as e:
        now = datetime.datetime.now()
        nowstr = now.strftime("%Y_%m_%d_%H_%M")
        with open(f"error_{nowstr}.txt", "a") as f:
            f.write(f"{nowstr}: {e}\n")

def main():
    load_dotenv()
    rawpage = get_rsc_rawsite()
    starttimes, nreservations = parse_rsc_page(rawpage)
    plotly_today(starttimes, nreservations)
    store_full_data(starttimes, nreservations)
    push_to_git()

if __name__ == "__main__":
    main()
