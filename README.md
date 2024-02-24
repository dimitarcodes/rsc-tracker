# rsc-tracker
Track how busy the Radboud Sportcentrum's gym is.

## Setup
* a machine that will run the logic (I use a raspberry pi 4 with pi os lite)
* python>=3.9
* pip
    * install requirements.txt
* create an ssh key and add it to github
    * add identity to pi's ssh config
* fill your credentials in the environment variables file
* create an sh script that runs smolscraper.py
* use crontab to run the sh script at desired times
    * each time slot stays visible until the last moment, so people can just reserve right before they want to enter, therefore I use
    ```29,59 6-23,1 * * * /path/to/script >> /path/to/log 2>&1``` 
    which means the script runs at every 29th and 59th minute (last minutes of the timeslots) every hour from 6 until 23 and at 1am, and the output is logged to a file

## How it works

### python scraper
* logs in RSC's website
* sends a form request to get the fitness reservation page
* finds the table with fitness timeslots and parses each entry by looking for the html table row tags
* collects the entries in json files
* pushes a json file with today's timeslots to github to be displayed on a static website running on github pages

## future development

### predictive models
* I'm collecting the full timeslots table which includes a few days from moment of request, so I can show how reservations change (people cancelling their reservations or signing up last second) and attempt to predict reservations using day of the week, approaching holidays etc.
* Field work - will go jim and count how many people are present (could also recruit friends) and attempt to train a model that predicts exact amount of people in the gym based on the reservations of past hour or two.

### prettier and responsive-er website
* tap on timeslot, see history of how reservations for it changed over time
* prettier chart overall
* change design depending on screen size (maybe use that dashboard js library?)

## Q&A

#### why the convoluted setup?
so basically, I'm cheap, so I don't want to pay a hosting website to run my tiny python script. Github offers free static hosting, which means it renders pages from a directory in your repo, but you can't make it run special logic/computations on their server. You can however push and rebuild your website ~10 times per hour (soft limit), which means I can just run my logic locally on my raspberry pi, collect the data I need in a json file and push it to github to re-build my website with updated data. (you can also do this from your pc obviously, I just wanted to mess around with my pi 4 which was collecting dust). Also originally used beautiful soup but then thought 'hm what if I eliminated 1 library requirement to KISS?'. You can totally use bs4 though, and it will probably be more robust

#### why not just ask the RSC for the data - you scan your card on a machine when you enter and leave so they must have the exact numbers

where's the fun in that?

