# Radboud SportsCenter Tracker

An application that periodically fetches the RSC Gym's reservations data, and plots it on a website.

## New Tech Stack Plan

* Airflow
    - for scheduling the ETL pipeline, ML model update, updating static website
* PostgreSQL
    - for backend of Airflow and storing reservation data
* GitHub Pages
    - for rendering the 'static' website
    - alternative - host on AWS
* Docker
    - for easy containerized deployment


## Old Tech Stack

* RaspberryPi 
    - runs everything locally
* crontab
    - for scheduling python ETL script, git script
* python
    - barebones script using default libraries
* json
    - store data in json files (semi-structured database)
