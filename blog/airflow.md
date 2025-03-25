# Airflow

While using airflow this is what I learned:

## First setup attempt

My intuition was to just install airflow and postgres locally and use them that way. I quickly ran into an issue - by default airflow only watches the global installation's DAG folder for DAGs.
This poses an obvious problem for development - you can't develop in a repo somewhere else and have airflow easily see the newest DAG you just wrote by default. There are 3 solutions to this:
* copy the DAG to the global DAGs folder - slow, inefficient, annoying
* simlink your dev folder to the global DAGs folder
* change the folder airflow watches for DAGs to your project folder
The latter 2 solutions are still annoying - you'd have to change this every time you start/switch working on a different project that needs airflow.
After scratching my head for a bit I realized airflow is probably meant to be ran in a docker container, which would only contain the project the airflow instance is meant for - and thus only the files it is concerned with.

## Using Airflow

* activate conda environment that airflow is installed in
* `airflow scheduler` to start the scheduler
* `airflow webserver` to activate the web interface

## Writing my first ETL DAG

### ETL (extract, transform, load)
ETL (extract, transform, load) pipelines are at the core of data engineering.
It makes sense to attempt to write a DAG that does these 3 tasks in sequence, in order to learn how to use airflow.
In the context of this application we can define the ETL process like this:
* Extract
    * access the RSC's website and obtain the relevant page's html
* Transform
    * parse the raw page to obtain the relevant data - the number of reservations for each timeslot
* Load
    * store the relevant results:
        * Final moment database - keeps track of the number of reservations 1 minute before the timeslot ends. Should be the most accurate historic information, as people can still sign up after the start of the timeslot (e.g. when they arrive at the RSC in the middle of a timeslot).
        * Continuous reservation information database - keeps track of all recorded numbers of reservation for each timeslot. It might be useful/interesting to keep track and explore how a single timeslot's reservations change over time - people signing up and cancelling their reservations.

### DAG (directed acyclic graph)
Airflow works through the definition of DAGs - directed acyclic graphs where each node is a task that needs to be executed.
The directed edges inform airflow what order the tasks need to be executed in.
There should be no cycles (hence acyclic), as airflow pipelines can't be infinite or get stuck in loops.

### Tasks in Airflow DAGs
Tasks should be self-contained operations, whose execution does not rely on each other beyond order.
In the context of ETL - each part can be seen as a different task.

### Problem - communicating data between tasks
Once a task has finished it often needs to pass data onto the next task.
E.g. the extract task in our app needs to pass on the raw html data it acquired to the transform task.
Turns out there's a few different ways to do this in Airflow, and the easiest solution is not always the most correct one.
Here's the options:
* use xcom
* use variables
* store intermediate data results on disk and run a cleanup task at the end to destroy irrelevant data

#### Variables
Variables are essentially a database managed by the Postgres backend to store variables (shocker) relevant to the DAG.
For example, they are used to store secrets (API keys, credentials) that can be accessed by the task when necessary.
They are not really meant to store data/intermediate results.

#### Xcom
Xcom is meant for passing metadata between tasks.
It is also a database managed by our Postgres backend - with a capacity of 1GB.
This is definitely enough for our usecase, however it is not its intended purpose.
Quite some solutions online suggest using it in this way, but really the way it's intended to be used is for the final solution.

#### Store intermediate data results
Each task should write its intermediate results to disk/S3, and pass the location/filepath of the data to the other tasks using Xcom.



