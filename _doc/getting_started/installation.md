---
layout: base
section: getting_started/installation
title: Installation
---
# How to install LazyBlacksmith

&nbsp;

## Requirements
* Python 2.7
* Celery 4
* Virtualenv (recommended)
* [NodeJS](http://nodejs.org/) + [Grunt-CLI](http://gruntjs.com/getting-started)
* Database connectors depending on the one you use (MySQL 5.6+,...)
* See [requirements.txt](https://github.com/Kyria/LazyBlacksmith/tree/master/requirements/) for other requirements
* (Optional/Recommended) Cache system (eg. python-memcached or redis-cache)
* (Optional) [Redis](http://redis.io/) for async tasks and queues (and cache)!
* Eve Online Icons (see CCP Icons part)

__Important:__ As we use Celery 4.x, it will not work on windows !

&nbsp;

## Installation

#### Environnement
Create your virtualenv and get LazyBlacksmith.
```sh
git clone https://github.com/Kyria/LazyBlacksmith.git
cd LazyBlacksmith
virtualenv env
```

Once your virtualenv is created, load it and install requirements
```sh
source env/bin/activate
pip install -r requirements/requirements.txt

# if you are using celery with redis (optional)
pip install -r requirements/requirements-celery-redis.txt
```

&nbsp;

#### Configs
You now need to create an application on [EVE Online Developpers](https://developers.eveonline.com/applications) to get CREST informations (secret key, client ID)

Once this is done, copy config.dist into config.py and edit the file.
Some mandatory informations :
```
DEBUG : True for dev, False for prod (require static compilation, see below)
SECRET_KEY : a secret key used for everything related to auth. Please change it !
SQLALCHEMY_DATABASE_URI : the database informations
USE_CCP_ICONS : True/False to display icons (read the CCP Icons chapter below)
CACHE_TYPE : leave 'null' if no cache, or set it your needs

---

Celery configs, use default config unless you know what you do.

---

ESI configs : set it with what you got/set before in CCP Developpers Application
```

&nbsp;

#### Init data
Now you set everything, it's time to "install" the database. This should create all the table in your database (if you get any errors, check you sqlalchemy informations)
```sh
python manage.py db upgrade
```

Update the SDE data by running the following command. It will download the latest from fuzzwork SDE Conversion and import them. 
```sh
python update_sde.py
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
PATH/TO/LazyBlacksmith/env/bin/celery multi start worker -A celery_app:celery_app -Q lbqueue -c5
```

Then in your crontab, you must schedule all these commands:
```sh
# to update character related data (every 5 min is enough)
python manage.py celery_task -c

# to update universe (prices, etc) related data (every hour is enough)
python manage.py celery_task -u

# to purge application useless data (once per day)
python manage.py celery_task -p
```

As these commands must be run within the virtualenv, it'd be better to encapsulated these commands within a script like:
```sh
#!/bin/bash
source PATH/TO/LazyBlacksmith/env/bin/activate

cd PATH/TO/LazyBlacksmith/
python manage.py celery_task -c
```

&nbsp;

##### Celery + Celery Beat (Scheduler)
There are multiple solution to run celery with celery beat. The example below are the minimal configurations.

You can celery with the -B option, to run beat and worker in the same time :
```
PATH/TO/LazyBlacksmith/env/bin/celery worker -A celery_app:celery_app -Q lbqueue -B -c5
```

Or you can run two daemons, one for celery beat, the other for the workers :
```sh
# celery beat
PATH/TO/LazyBlacksmith/env/bin/celery beat -A celery_app:celery_app -Q lbqueue

# celery workers
PATH/TO/LazyBlacksmith/env/bin/celery multi start worker -A celery_app:celery_app -Q lbqueue -c5
```


&nbsp;

## CCP Icons

If you set ```USE_CCP_ICONS = True``` you need to download the files "EVE_VERSION_Types.zip" from [CCP Toolkit](https://developers.eveonline.com/resource/resources)

Then move the files into ```lazyblacksmith/static/ccp/``` (as a result, you should have ```lazyblacksmith/static/ccp/Types/files.png```)

