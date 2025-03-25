# Implementing ETL pipeline with Airflow, PostgreSQL, Spark

## Introduction
I wanted to practice using industry-standard technologies, instead of barebones systems that 'just get the job done'.

## Original setup
Originally this webscraper and visualization app was setup this way:

* barebones python script:
    1. extracts raw html data by scraping the sportcenter's website with `requests`
    2. transforms the raw html page into a dictionary (json) dataset using simple `find` methods
    3. loads the data by saving the json with the information we're interested in
* sh script to interact with git
    * commits and pushes new json data file
* crontab job
    * runs the barebones python script every 15 mins - at :14,:29, :44, :59 of every hour - a minute before the end of each timeslot that can be reserved
    * if successful, runs sh script to push new data with git
* github pages
    * renders a static website, updated by updating the json file in the repository

## New setup plan

### Technologies I want to use

* Airflow
    * controls the execution of ETL pipeline
* PostgreSQL
    * for storing historical data
    * for backend of airflow
* Spark
    * for conducting the ETL job
    * for training a ML predictive model
* containerization with Docker
    * easier setup and deployment on new systems (AWS/raspberryPi/old laptop)
    * easier way for other people to run their own instance

### Requirements

* once I'm done with this project I want to publish it on docker's repository of images, so it can be setup and run in 1 command
* need to keep secrets (RSC login) from being exposed
* want to attempt predictive modelling of future reservations (how busy it will be)

## Process of implementing new setup:

### Installing airflow
Pretty straightforward, just use pip.

### Installing PostgreSQL
Use apt

### 