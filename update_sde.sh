#!/bin/bash

command -v bunzip2 >/dev/null 2>&1
if [[ $? -ne 0 ]]
then
    echo "bunzip2 is required to unzip SDE, please install it!"
    exit 1
fi 

echo -en "Downloading latest sqlite SDE from fuzzwork.co.uk ... "
wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2 >/dev/null 2>&1
if [[ $? -ne 0 ]]
then
    echo "[FAILED]"
    echo "An error occured, please download manually latest sqlite SDE here https://www.fuzzwork.co.uk/dump"
    echo "Then run 'python manage.py sde_import -d sqlite-latest.sqlite' after unzipping it"
    exit 2
else
    echo "[SUCCESS]"
    echo -ne "Unzipping file..."
    bunzip2 -f sqlite-latest.sqlite.bz2 >/dev/null 2>&1
    if [[ $? -ne 0 ]]
    then
        echo "[FAILED]"
        echo "Something wrong happend, please unzip manually the file"
        echo "Then run 'python manage.py sde_import -d sqlite-latest.sqlite'"
    else
	echo "[SUCCESS]"
    fi
fi

echo "Testing if in virtualenv"
python -c 'import lazyblacksmith.app' >/dev/null 2>&1
if [[ $? -eq 0 ]]
then
    echo "Importing SDE"
    python manage.py sde_import -d sqlite-latest.sqlite
else
    echo "You are not in the virtualenv for lazyblacksmith"
    echo "Please activate your virtualenv and run 'python manage.py sde_import -d sqlite-latest.sqlite'"
fi
