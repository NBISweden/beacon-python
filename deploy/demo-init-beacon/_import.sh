#!/bin/bash
set +x

psql -h 130.238.239.160 -U beacon -p 5432 beacondb < /mnt/beacon_testdata.psql
