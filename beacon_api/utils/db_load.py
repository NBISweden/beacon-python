"""Beacon Database Loader."""

# TO DO
# 1. Look into async generators, to send smaller chunks from load_datafile() to insert_variants()
# 2. Add feature to parse .vcf.gz files in addition to .vcf files to conserve disk space
# 3. Multithreading for large files

import os
import argparse
import json

import asyncio
import asyncpg
import vcf

from datetime import datetime

from ..conf.config import DB_URL
from .logging import LOG


class BeaconDB:
    """Database connection and operations."""

    def __init__(self, db_url):
        """Start database routines."""
        LOG.info('Start database routines')
        self._conn = None
        try:
            LOG.info('Fetch database URL from config')
            self._db_url = db_url
            LOG.info('Database URL has been set -> Connections can now be made')
        except Exception as e:
            LOG.error(f'ERROR FETCHING DB URL -> {e}')

    async def connection(self):
        """Connect to the database."""
        LOG.info('Establish a connection to database')
        try:
            self._conn = await asyncpg.connect(self._db_url)
            LOG.info('Database connection has been established')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CONNECT TO DATABASE -> {e}')

    async def check_tables(self, desired_tables):
        """Check that correct tables exist in the database."""
        LOG.info('Request tables from database')
        found_tables = []
        tables = await self._conn.fetch("""SELECT table_name
                                        FROM information_schema.tables
                                        WHERE table_schema='public'
                                        AND table_type='BASE TABLE';""")
        LOG.info('Tables received -> check that correct tables exist')
        for table in list(tables):
            found_tables.append(dict(table)['table_name'])
        missing_tables = list(set(desired_tables) - set(found_tables))
        for table in found_tables:
            LOG.info(f'{table} exists')
        for table in missing_tables:
            LOG.error(f'{table} is missing!')
        return missing_tables

    async def create_tables(self, sql_file):
        """Create tables to database according to given schema."""
        LOG.info(f'Create tables to database according to given schema in file {sql_file}')
        try:
            with open(sql_file, 'r') as file:
                schema = file.read()
            await self._conn.execute(schema)
            LOG.info('Tables have been created')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CREATE TABLES -> {e}')

    async def load_metadata(self, metafile, datafile):
        """Parse metadata from a JSON file and insert it into the database."""
        metadata = {}
        try:
            LOG.info(f'Calculate number of samples from {datafile}')
            sample_count = 0
            with open(datafile, 'r') as df:
                # calculate number of unique test subjects
                sample_count = len(vcf.Reader(df).samples)
            LOG.info(f'Parse metadata from {metafile}')
            with open(metafile, 'r') as metafile:
                metadata = json.load(metafile)
            LOG.info('Metadata has been parsed')
            try:
                LOG.info(f'Attempting to insert metadata to database')
                await self._conn.execute("""INSERT INTO beacon_dataset_table
                                         (name, datasetId, description, assemblyId,
                                         createDateTime, updateDateTime, version,
                                         sampleCount, externalUrl, accessType)
                                         VALUES
                                         ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)""",
                                         metadata['name'], metadata['datasetId'],
                                         metadata['description'], metadata['assemblyId'],
                                         datetime.strptime(metadata['createDateTime'], '%Y-%m-%d %H:%M:%S'),
                                         datetime.strptime(metadata['updateDateTime'], '%Y-%m-%d %H:%M:%S'),
                                         metadata['version'], sample_count,
                                         metadata['externalUrl'], metadata['accessType'])
            except Exception as e:
                LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO INSERT METADATA -> {e}')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO PARSE METADATA -> {e}')
        return metadata['datasetId']

    async def load_datafile(self, datafile, dataset_id):
        """Parse data from datafile and send it to be inserted."""
        LOG.info(f'Read data from {datafile}')
        db_queue = []  # TO DO: Look into chunking this to smaller bits (async generator)
        try:
            with open(datafile, 'r') as data:
                LOG.info('Generate database queue')
                db_queue = [record for record in vcf.Reader(data)]
                LOG.info(f'Send {len(db_queue)} variants for insertion')
                return dataset_id, db_queue
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE GENERATING DB QUEUE -> {e}')

    async def insert_variants(self, dataset_id, variants):
        """Insert variant data to the database."""
        LOG.info(f'Received {len(variants)} variants for insertion to {dataset_id}')
        try:
            async with self._conn.transaction():
                LOG.info('Insert variants into the database')
                for variant in variants:
                    await self._conn.execute("""INSERT INTO beacon_data_table
                                             (datasetId, chromosome, start, reference, alternate,
                                             "end", variantType, variantCount, callCount, frequency)
                                             SELECT ($1), ($2), ($3), ($4), alt, ($6), ($7), ($8), ($9), freq
                                             FROM unnest($5::varchar[]) alt, unnest($10::float[]) freq""",
                                             dataset_id, variant.CHROM, variant.POS, variant.REF,
                                             [str(alt) for alt in variant.ALT], variant.end,
                                             variant.var_type, variant.num_hom_alt, variant.num_called,
                                             [float(freq) for freq in variant.aaf])
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO INSERT VARIANTS -> {e}')

    async def close(self):
        """Close the database connection."""
        try:
            LOG.info('Mark the database connection to be closed')
            await self._conn.close()
            LOG.info('The database connection has been closed')
        except Exception as e:
            LOG.error(f'AN ERROR OCCURRED WHILE ATTEMPTING TO CLOSE DATABASE CONNECTION -> {e}')


async def init_beacon_db(arguments=None):
    """Run database operations here."""
    # Fetch command line arguments
    args = parse_arguments(arguments)

    # Initialise the database connection
    db = BeaconDB(DB_URL)

    # Connect to the database
    await db.connection()

    # Check that desired tables exist (missing tables are returned)
    tables = await db.check_tables(['beacon_dataset_table', 'beacon_data_table'])

    # If some tables are missing, run init.sql to recover them
    if len(tables) > 0:
        await db.create_tables(os.environ.get('TABLES_SCHEMA', 'init.sql'))

    # Insert dataset metadata into the database, prior to inserting actual variant data
    dataset_id = await db.load_metadata(args.metadata, args.datafile)

    # Insert data into the database
    data = await db.load_datafile(args.datafile, dataset_id)
    await db.insert_variants(dataset_id=data[0], variants=data[1])

    # Close the database connection
    await db.close()


def parse_arguments(arguments):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="""Load datafiles with associated metadata
                                     into the beacon database. See example data and metadata files
                                     in the /data directory""")
    parser.add_argument('datafile',
                        help='.vcf file containing variant information')
    parser.add_argument('metadata',
                        help='.json file containing metadata associated to datafile')
    return parser.parse_args(arguments)


def main():
    """Run the magic."""
    # TO DO add this to setup to run from command line
    # allow arguments to be passed from command line
    asyncio.get_event_loop().run_until_complete(init_beacon_db())
    # TO DO Python3.7 will become that
    # maybe we should move to 3.7
    # asyncio.run(main())


if __name__ == "__main__":
    main()
