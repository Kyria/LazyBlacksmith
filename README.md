# LazyBlacksmith

![Logo](https://raw.githubusercontent.com/Kyria/LazyBlacksmith/new-theme/lazyblacksmith/static/img/logo128.png)

An EVE Online Industry application for lazy people.


## About
LazyBlacksmith is a flask application allowing people to get informations about industry in eveonline.

#### Features
* Blueprints
 * Manufacturing informations including components required and installation costs
 * Research data for material and time efficiency (time, cost)
 * Invention informations for components and costs.
* Get and compare item price over all regions

#### CREST (as batch or through celery)
* Use CREST market price / adjusted price for costs
* Use CREST industry index for installation fee

#### TODO
* Ore refining and compression (see branch ore_refining_compression)
 * View refining table
 * Calculate compression from user needs (in materials) and using defaults ore
  * Also allow to manually select what ore we want to use to compress
* Permalinks in manufacturing / research / production
* Link API key to user account (CREST Login) to get, save and configure existing blueprints, with their ME/TE for direct use in manufacturing / invention



## Requirements
* Python 2.7
* Virtualenv (recommended)
* [NodeJS](http://nodejs.org/) + [Grunt-CLI](http://gruntjs.com/getting-started)
* Database connectors depending on the one you use (MySQL 5.6+,...)
* See [requirements.txt](requirements/) for other requirements
* (Optional/Recommended) Cache system (eg. python-memcached or redis-cache)
* (Optional) [Redis](http://redis.io/) for async tasks and queues (and cache)!
* Eve Online Icons (see CCP Icons part)



## Installation

#### Environnement
Create your virtualenv and get LazyBlacksmith.
```shell
git clone https://github.com/Kyria/LazyBlacksmith.git
cd LazyBlacksmith
virtualenv env
```

Once your virtualenv is created, load it and install requirements
```
# in windows, type env/Script/activate
source env/bin/activate
pip install -r requirements/requirements.txt

# if you are using celery with redis
pip install -r requirements/requirements-celery-redis.txt
```

#### Configs
You now need to create an application on [EVE Online Developpers](https://developers.eveonline.com/applications) to get CREST informations (secret key, client ID)

Once this is done, copy config.dist into config.py and edit the file.
Some mandatory informations :
```
DEBUG : True for dev, False for prod (require static compilation, see below)
SQLALCHEMY_DATABASE_URI : the database informations
USE_CCP_ICONS : True/False to display icons (read the CCP Icons chapter below)
CACHE_TYPE : leave 'null' if no cache, or set it your needs

Celery configs, if you don't use it, leave them like that

CREST API informations : set it with what you got/set before in CCP Developpers Application
```

#### Init data
Now you set everything, it's time to "install" the database. This should create all the table in your database (if you get any errors, check you sqlalchemy informations)
```
python manage.py db upgrade
```

Download the latest SDE conversion from fuzzwork in sqlite [here](https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2) unzip it then load it with :
```
python manage.py sde_import -d path/to/sqlite-latest.sqlite
```

If you also want to have some CREST data right now, you can run the following commands :
```
python manage.py celery_task -a update_adjusted_price
python manage.py celery_task -a update_industry_index
python manage.py celery_task -a update_market_price
```

#### Static file compilation
If you are using it in production environnement, or upgrading your installation, you need to remake all static files (css/js). For this, first do ```npm install``` to install all the nodejs required package, then type ```grunt``` to compile the static files.

#### CREST / API
To update the CREST data, you have 2 solutions :
* run them directly, as you did in the "init data" part
* use celery

##### Celery + Celery Beat (Scheduler)
There are multiple solution to run celery with celery beat. The example below are the minimal configurations.

You can celery with the -B option, to run beat and worker in the same time :
```
PATH/TO/LazyBlacksmith/env/bin/celery worker -A celery_app:celery_app -B -c5
```

Or you can run two daemons, one for celery beat, the other for the workers :
```
# celery beat
PATH/TO/LazyBlacksmith/env/bin/celery beat -A celery_app:celery_app

# celery workers
PATH/TO/LazyBlacksmith/env/bin/celery multi start worker -A celery_app:celery_app -c5
```



## CCP Icons

If you set ```USE_CCP_ICONS = True``` you need to download the files "EVE_VERSION_Types.zip" from CCP Toolkit ; https://developers.eveonline.com/resource/resources and then
move the files into ```lazyblacksmith/static/ccp/``` (as a result, you should have ```lazyblacksmith/static/ccp/Types/files.png```)



## Contact
Guillaume B.
* Github: @Kyria
* [TweetFleet Slack](https://www.fuzzwork.co.uk/tweetfleet-slack-invites/): @althalus
* Eveonline: Althalus Stenory



## LazyBlacksmith License
Copyright (c) 2015, Guillaume
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of LazyBlacksmith nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



## EVE Online / CCP License
EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf. CCP hf. has granted permission to LazyBlacksmith to use EVE Online and all associated logos and designs for promotional and information purposes on its website but does not endorse, and is not in any way affiliated with, LazyBlacksmith. CCP is in no way responsible for the content on or functioning of this website, nor can it be liable for any damage arising from the use of this website.
