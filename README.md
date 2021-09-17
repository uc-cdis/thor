# Thor
The Gen3 Release Orchestrator

<img src="/images/logo.png" alt="drawing" width="250"/>

_Image by [cromaconceptovisual](https://pixabay.com/users/cromaconceptovisual-4595909) from [Pixabay](https://pixabay.com/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=4898879)_

# Overview

this new tool should help us achieve a fully-automated hands-free Gen3 release. We need to eliminate “toil” from our day-to-day tasks so we can focus on project-specific tasks, maintenance of our CI/CD pipelines, expansion of the Gen3-QA framework, test coverage and innovation.

Manual and repetitive work is boring and error-prone, as software engineers, we can do better than this.


# Features

This new tool (THOR) has the following features:
* RESTful API to start the release flow and track the status of each step
* Coordinate each and every step of the Gen3 Release by working with:
  * The Jenkins API (kicking off Jenkins jobs and tracking its results)
  * Executing gen3-release-utils scripts & the gen3release-sdk CLI
  * Interacting with JIRA and Slack APIs
* Provide FULL transparency to the Gen3 Release process through a friendly GUI that should help any Project Manager (PM) observe the progress of the releases throughout the environments they own.
* Facilitate parameterization of our release automation and make it more flexible (e.g., change cadence / time-frame between releases).

# High-level overview

Thor will execute a series of steps based on a monthly release cycle. 

In the diagram below, solid lines indicate sequential execution, while dotted lines indicate dependency of some sort.


<img src="/images/thor_step_flowchart.PNG" alt="drawing" width="500"/>


Thor is currently centered around a monthly release cycle, but is designed to be more flexible in the future. 

The key features of the cycle are the feature freeze, which occurs on the second Friday of each month, and the code freeze, which occurs on the fourth Friday of each month. 

On the second Friday of each month, Thor will automatically create a Release in JIRA, and will split off an integration branch within Github. 

After splitting the integration branch, Thor will perform load tests via a Jenkins interface, and automatically generate release notes. 

On the fourth Friday of each month, the integration branch is merged into the stable branch on Github, and the release is marked as Released on Jira. 

This new code can then be adopted by the existing userbase. 

# How to run Thor

## Create the database

```
psql -U postgres -c "create database thor_test_tmp"
```

## Create tables and test data

```
poetry run python src/thor/create_all_tables.py
```

You should see something like:

```
% psql -U postgres
psql (13.3)
Type "help" for help.

postgres=# \c thor_test_tmp;
You are now connected to database "thor_test_tmp" as user "postgres".
thor_test_tmp=# \dt;
          List of relations
 Schema |   Name   | Type  |  Owner
--------+----------+-------+----------
 public | releases | table | postgres
 public | tasks    | table | postgres

thor_test_tmp=# select * from releases;
 id | version |   result
----+---------+-------------
  3 | 2021.09 | In Progress
  4 | 2021.07 | Completed
(2 rows)
```

## How to test

```
poetry run pytest -vv -s tests
```

## Start the FastAPI web server

```
poetry run gunicorn thor.main:app -b 0.0.0.0:6565 -k uvicorn.workers.UvicornWorker --reload
```

## Time travel

```
LD_PRELOAD=/libfaketime/src/libfaketime.so.1 FAKETIME="-15d" poetry run gunicorn thor.main:app -b 0.0.0.0:6565 -k uvicorn.workers.UvicornWorker --reload
```
or
```
LD_PRELOAD=/libfaketime/src/libfaketime.so.1 FAKETIME="@2020-12-24 20:30:00" poetry run gunicorn thor.main:app -b 0.0.0.0:6565 -k uvicorn.workers.UvicornWorker --reload
```
