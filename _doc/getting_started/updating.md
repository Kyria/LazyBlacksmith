---
layout: base
section: getting_started/updating
title: Updating LB
---
# Updating LB

<div class="alert alert-dismissible alert-danger">
    <strong>Change 01/01/2020:</strong> Since this date, the migration folder have changed (due to all errors, it was easier to remake it from scratch).
    <br>
    If you already used the application and need to upgrade, please edit your `alembic_version" table, and set the "version_num" column to "1". This will allow you to use the new migration scripts.
</div>

To update the application, simply update the files then run the following:
```bash
# get into the virtualenv
source env/bin/activate

# update the DB
python manage.py db upgrade
# update the static files
npm run dist
# update the SDE
python manage.py sde_import -d
```