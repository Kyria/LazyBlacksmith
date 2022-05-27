---
layout: base
section: getting_started/installation
title: Installation
---
# How to install LazyBlacksmith

&nbsp;

## Requirements
* Python 3.7+
* Celery 5
* Celery Beat or manual trigger for tasks
* Virtualenv (recommended)
* [NodeJS](http://nodejs.org/)
* Database connectors depending on the one you use (Validated for postgresql and mysql/mariadb)
* See [requirements.txt](https://github.com/Kyria/LazyBlacksmith/tree/master/requirements/) for other requirements
* (Optional/Recommended) Cache system, see [Flask-Caching](https://pythonhosted.org/Flask-Caching/)
* Eve Online Icons (see CCP Icons part)

__Important:__ As we use Celery 5, it may not work on windows !

&nbsp;

## Installation

#### Environnement
Create your virtualenv and get LazyBlacksmith.
```bash
git clone https://github.com/Kyria/LazyBlacksmith.git
cd LazyBlacksmith
virtualenv env
```

Once your virtualenv is created, load it and install requirements
```bash
source env/bin/activate
pip3 install -U -r requirements/global-requirements.txt
# If you want to use MySQL, add the following requirements
pip3 install -U -r requirements/mysql-requirements.txt
# If you want to use PostgreSQL, add the following requirements
pip3 install -U -r requirements/postgresql-requirements.txt
```

&nbsp;

#### Configs
You now need to create an application on [EVE Online Developpers](https://developers.eveonline.com/applications) to get ESI informations (secret key, client ID)

Once this is done, copy config.dist into config.py and edit the file with the right information everywhere.
```bash
cp config.dist config.py
```

** Celery configuration is mandatory if you use it. Cache is highly recommended **

&nbsp;

#### Setup the database
Now you set everything, it's time to "install" the database. This should create all the table in your database (if you get any errors, check you sqlalchemy informations)
```sh
python manage.py db upgrade
```

Update the SDE data by running the following command. It will download the latest from fuzzwork SDE Conversion and import them.
```sh
python manage.py sde_import -d
```

&nbsp;

#### Static file compilation
If you are using it in production environnement, or upgrading your installation, you need to remake all static files (css/js).

```sh
# to install all the nodejs required package.
npm install
# to compile files
npm run dist
```

__If you are doing development__ you can do the same, or you can `npm run watch` which will watch for changes while you dev and recompile files when necessary.

&nbsp;

#### ESI
To update the ESI data, you have 2 solutions :
* Use celery as worker and run the task with some scheduler like CRONTAB
* Use celery with celery beat (its own scheduler)

&nbsp;

##### Celery + Crontab

If you want to run celery tasks with crontab, you first need to start a celery worker :
```sh
# THIS IS ONLY AN EXAMPLE !
PATH/TO/LazyBlacksmith/env/bin/celery -A app_celery:celery_app  worker-c5
```

Then in your crontab, you must schedule all these commands:
```sh
# to update character related data (every 5 min is enough)
python celery_cli.py celery_tasks -c

# to update universe (prices, etc) related data (every hour is enough)
python celery_cli.py celery_tasks -u

# to purge application useless data (once per day)
python celery_cli.py celery_tasks -p
```

As these commands must be run within the virtualenv, it'd be better to encapsulated these commands within a script like:
```sh
#!/bin/bash
source PATH/TO/LazyBlacksmith/env/bin/activate

cd PATH/TO/LazyBlacksmith/
python celery_cli.py celery_tasks -c
```

&nbsp;

##### Celery + Celery Beat (Scheduler)
There are multiple solution to run celery with celery beat. The example below are the minimal configurations.

You can celery with the -B option, to run beat and worker in the same time :
```
PATH/TO/LazyBlacksmith/env/bin/celery -A app_celery:celery_app worker -B -c5
```

Or you can run two daemons, one for celery beat, the other for the workers :
```sh
# celery beat
PATH/TO/LazyBlacksmith/env/bin/celery -A app_celery:celery_app beat

# celery workers
PATH/TO/LazyBlacksmith/env/bin/celery -A app_celery:celery_app worker -c5
```


&nbsp;

## CCP Icons

If you set ```USE_CCP_ICONS = True``` you will use the images from ```images.evetech.net```

