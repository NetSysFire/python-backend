#!/bin/bash

# DO NOT run this script during an active tournament. This will
# perform a full reset of the scoreboard database.

. secrets.sh
./manage.py wipe_db --all
./manage.py migrate scoreboard zero && rm -r scoreboard/migrations/* && \
    ./manage.py makemigrations scoreboard && ./manage.py migrate scoreboard
