#!/bin/sh

swefreq_host=dev-swefreq-db
beacon_db=beacon

# Migrates the beacon views/tables from the "swefreq" PostgreSQL
# database on $swefreq_host to a local PostgreSQL database ($beacon_db).
#
# This script assumes that it has been checked out as part of the NBIS
# fork of the CSCfi beacon-python Github repository and that it has
# access to "data/init.sql" from its current directory.
#
# It further assumes that access to the "swefreq" database on
# $swefreq_host is possible and that the current user can drop and
# create the $beacon_db database locally.
#
# WARNING:
#       The local database $beacon_db is dropped and recreated.
#
#       The migration of the "beacon_data_table" table is currently
#       limited to 100k records.
#
# ISSUES:
#       The column "aggregatedVariantType" is missing from the
#       beacon.beacon_data_table table in the Swefreq schema.  Its
#       values are currently replaced by NULLs in the local $beacon_db
#       database.

# Initialise local database.
dropdb "$beacon_db"
createdb "$beacon_db"
psql "$beacon_db" <data/init.sql

# Copy data, one table at a time.

# beacon_dataset_table:
psql --host="$swefreq_host" --user=swefreq swefreq --command='
	COPY (SELECT
		index,name,datasetId,description,assemblyId,
		creationDateTime,updateDateTime,version,sampleCount,
		externalUrl, accessType
	FROM beacon.beacon_dataset_table) TO STDOUT' |
psql "$beacon_db" --command='
	COPY beacon_dataset_table FROM STDIN'

# beacon_dataset_counts_table
# Don't copy column "dataset".
psql --host="$swefreq_host" --user=swefreq swefreq --command='
	COPY (SELECT
		datasetId,callCount,variantCount
	FROM beacon.beacon_dataset_counts_table) TO STDOUT' |
psql "$beacon_db" --command='
	COPY beacon_dataset_counts_table FROM STDIN'

# beacon_data_table
# Order of columns are different, and "aggregatedVariantType" is missing
# in SweFreq database (replace with NULL).
psql --host="$swefreq_host" --user=swefreq swefreq --command='
	COPY (SELECT
		index,datasetId,start,chromosome,reference,alternate,"end",
		NULL,alleleCount,callCount,frequency,variantType
	FROM beacon.beacon_data_table LIMIT 100000) TO STDOUT' |
psql "$beacon_db" --command='
	COPY beacon_data_table FROM STDIN'

# beacon_mate_table
# Don't copy column "variantType".
psql --host="$swefreq_host" --user=swefreq swefreq --command='
	COPY (SELECT
		index,datasetId,chromosome,chromosomeStart,chromosomePos,
		mate,mateStart,matePos,reference,alternate,alleleCount,
		callCount,frequency,"end"
	FROM beacon.beacon_mate_table) TO STDOUT' |
psql "$beacon_db" --command='
	COPY beacon_mate_table FROM STDIN'

echo Done.
