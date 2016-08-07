# LazyBlacksmith
An EVE Online Industry application for lazy people.

## About
LazyBlacksmith is a flask application allowing people to get informations about industry in eveonline.

#### Features
* Blueprint manufacture informations including components required and installation costs
 * Use CREST market price / adjusted price for costs
 * Use CREST industry index for installation fee

#### TODO
* Blueprint research and inventions informations
* Things.

## Requirements
* Python 2.7
* [Redis](http://redis.io/) for async tasks and queues (and cache)!
* [NodeJS](http://nodejs.org/) + [Grunt-CLI](http://gruntjs.com/getting-started)
* Virtualenv (recommended)
* Cache system (eg. python-memcached or redis-cache) (recommanded)
* Database connectors depending on the one you use (MySQL 5.6+,...)
* See [requirements.txt](requirements.txt) for other requirements
* Eve Online Icons (see CCP Icons part)

## Installation

Comin'... one day or another :)

## Contact
Guillaume B.
* Github: @Kyria
* [TweetFleet Slack](https://www.fuzzwork.co.uk/tweetfleet-slack-invites/): @althalus

## CCP Icons

If you set ```USE_CCP_ICONS = True``` you need to download the files "EVE_VERSION_Types.zip" from CCP Toolkit ; https://developers.eveonline.com/resource/resources and then
move the files into ```lazyblacksmith/static/ccp/``` (as a result, you should have ```lazyblacksmith/static/ccp/Types/files.png```)

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
