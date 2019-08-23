#!/usr/bin/env bash

docker run -ti -v "$PWD":/mnt postgres:11.2 bash /mnt/import.sh
