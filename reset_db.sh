#!/bin/bash

# This does NOT do a full reset for next year's tournament. It is for when a
# model has just been changed and you want to recreate the database with that
# new structure.
. secrets.sh
./manage.py migrate scoreboard zero && rm -r scoreboard/migrations/* && \
    ./manage.py makemigrations scoreboard && ./manage.py migrate scoreboard
