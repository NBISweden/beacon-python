# beacon-python
[Beacon API specifications](https://github.com/ga4gh-beacon/specification/blob/release-1.0.0/beacon.md)


## Table of content
- [About](#about)
  * [What is a Beacon?](#what-is-a-beacon-)
- [Requirements](#requirements)
- [Quick start](#quick-start)
  * [Create database](#create-database)
  * [Run the application](#run-the-application)
- [Using the application](#using-the-application)
- [Further information](#further-information)
  * [Project structure](#project-structure)
  * [Testing](#testing)

## About

### What is a Beacon?

The Beacon project was launched in 2014 to show the willingness of researchers to enable the secure sharing of genomic data from participants of genomic studies. Beacons are web-servers that answer questions such as Does your dataset include a genome that has a specific nucleotide (e.g. G) at a specific genomic coordinate (e.g. Chr.1 position 111,111)? to which the Beacon must respond with yes or no, without referring to a specific individual.


## Requirements
* Python 3.6
* PostgreSQL Server 9.0+

## Quick start

### Create database

In the application we use PostgreSQL but other databases will work as well. Install a PostgreSQL version
higher than 9 and use the `psql`command line tool. For this example we will create a simple database without
a specified user or password. The database name will be set to `beacondb`.

A prerequisite is that PostgreSQL server is running. Then open the the `psql` command line tool with the default `postgres`.
```
$ psql postgres
```
Use the `CREATE DATABASE` command to create the database called `beacondb`:
```
postgres=# CREATE DATABASE beacondb;
```
* You can list the available databases with the command `\l` and to exit into the normal terminal view write `\q` or press `CTRL + D`.
* To view the tables in the database use the command `\dt`
* To view the columns of a table write `\d table_name`

### Run the application

Create a virtual environment for the application:
```
$ virtualenv env
```
`cd` into the new `env` directory and activate the virtual environment:
```
$ cd env
```
```
$ . bin/activate
```
Clone the code into the directory:
```
git clone https://github.com/CSCfi/beacon-python.git
```


Install all the necessary dependencies to the virtual env from the `requirenments.txt` file using pip:

```
cd beacon-python
pip3 install -r requirements.txt
```
##### Environment Variables
| ENV | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql://localhost:5432` | The URL for the PostgreSQL server where the database is served. |
| `DATABASE_NAME` | `beacondb` | Name of the database. |
| `DATABASE_USER` | `` | Username configured for the database. |
| `DATABASE_PASSWORD` | `` | Password configured for the database. |
| `HOST` | `0.0.0.0` | Host set for Flask in the wsgi file. |
| `PORT` | `8080` | The port defined for Flask in wsgi file. |
| `DEBUG` | `True` | If set to `True`, Flask will print events into the terminal. |
| `LOGGING_LVL` | `DEBUG` | The logging level that will be set for the application. Can be: [`DEBUG`, `INFO`, `WARNIG`, `CRITICAL`] |

Set the necessary environment variables. If you haven't configured a user and a password for the database you should set them as empty:
```
$ export DATABASE_URL=postgresql://localhost:5432
$ export DATABASE_NAME=beacondb
$ export DATABASE_USER=
$ export DATABASE_PASSWORD=
$ export HOST=0.0.0.0
$ export PORT=8080
$ export DEBUG=True
$ export LOGGING_LVL=DEBUG
```

To run the application:

```
$ pip3 install .
$ beacon
```

To test the application you can either use `curl` in the command line like in examples or just by typing the address into the browser.

* [http://localhost:8080/](http://localhost:8080/)

* [http://localhost:8080/query?referenceName=1&start=2947950&referenceBases=A&alternateBases=G&assemblyId=GRCh37&includeDatasetResponses=ALL](http://localhost:8080/query?referenceName=1&start=2947950&referenceBases=A&alternateBases=G&assemblyId=GRCh37&includeDatasetResponses=ALL)

Deactivate the virtual environment with the command:
```
$ deactivate
```
## Configure database

### Create tables

The application is using the object relational mapper (ORM) SQLAlchemy to handle much of the communication
between the application and the database, and that is why the database tables are created using SQLAlchemy.
So instead of manually creating the PostgreSQL tables using `psql` in the command line, the tables are
created by calling the `db.create_all` method that uses the `db` object from SQLAlchemy. To call the method we
use the Python shell in the command line.


Open the Python shell in the command line:
```Shell
$ python3
```
Create the tables:
```python
>>> from beacon_api.conf.config import db
>>> db.create_all()
>>> exit()
```

This will create the database tables according to the schema specified in `utils/models.py`.

### Load data

In this example we will fill the `genomes` table first, the order you fill the tables in does not matter
because the tables does not have any direct relations. In the example we load three data sets to the database.

The table needs in the first column the `id`, witch is a number starting from one and iterates with +1 for every row.
If the data sets you are loading don't have this `id` in the first row you can add it the following way.

```Shell
$ awk '{printf "%s;%s\n", NR,$0}' data/dataset1.csv > dataset1_.csv
$ awk '{printf "%s;%s\n", NR+72,$0}' data/dataset2.csv > dataset2_.csv
$ awk '{printf "%s;%s\n", NR+161,$0}' data/dataset3.csv > dataset3_.csv
```

The table column `dataset_id` is the name of the table. If the file that you are loading does not have the right name in
that column you can change it using:

```Shell
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET1";print $0}' dataset1_.csv > set1.csv
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET2";print $0}' dataset2_.csv > set2.csv
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET3";print $0}' dataset3_.csv > set3.csv
```

Then we load the `genomes` table with the files. Open `psql` in the command line:

```Shell
$ psql beacondb
```
Copy the files into the table(use the correct path):

```SQL
beacondb=# COPY genomes FROM '/opt/app-root/files/set1.csv' DELIMITER ';' CSV;
beacondb=# COPY genomes FROM '/opt/app-root/files/set2.csv' DELIMITER ';' CSV;
beacondb=# COPY genomes FROM '/opt/app-root/files/set3.csv' DELIMITER ';' CSV;
```

Then we check for the right values to fill in the beacon_dataset_table in the `variantCount` and `callCount`:

````Shell
$ awk -F ';' '{SUM+=$10}END{print SUM}' set1.csv			#variantCount
$ awk -F ';' '{SUM+=$11}END{print SUM}' set1.csv			#callCount
````
variantCount = 6966, callCount = 360576 for set1.csv
```Shell
$ awk -F ';' '{SUM+=$10}END{print SUM}' set2.csv			#variantCount
$ awk -F ';' '{SUM+=$11}END{print SUM}' set2.csv			#callCount
```
variantCount = 16023, callCount = 445712 for set2.csv
```Shell
$ awk -F ';' '{SUM+=$10}END{print SUM}' set3.csv			#variantCount
$ awk -F ';' '{SUM+=$11}END{print SUM}' set3.csv			#callCount
```
variantCount = 20952, callCount = 1206928 for set3.csv


Lastly we fill the `beacon_dataset_table` with the right info for the different datasets. You can
either fill it using the method `load_dataset_table()` in `models.py`, or by using `psql` from the
command line.

Using `load_dataset_table()`in python shell:
```python
from beacon_api.utils.models import load_dataset_table

load_dataset_table('DATASET1', 'example dataset number 1', 'GRCh38', 'v1', 6966, 360576, 1, 'externalUrl', 'PUBLIC')
load_dataset_table('DATASET2', 'example dataset number 2', 'GRCh38', 'v1', 16023, 445712, 1, 'externalUrl', 'PUBLIC')
load_dataset_table('DATASET3', 'example dataset number 3', 'GRCh38', 'v1', 20952, 1206928, 1, 'externalUrl', 'PUBLIC')
```

Using `psql` in command line:
```SQL
INSERT INTO beacon_dataset_table (name, description, assemblyId, createDateTime, updateDateTime, version, variantCount, callCount, sampleCount, externalUrl, accessType) VALUES ('DATASET1', 'example dataset number 1', 'GRCh38', 'v1', 6966, 360576, 1, 'externalUrl', 'PUBLIC');

INSERT INTO beacon_dataset_table (name, description, assemblyId, createDateTime, updateDateTime, version, variantCount, callCount, sampleCount, externalUrl, accessType) VALUES ('DATASET2', 'example dataset number 2', 'GRCh38', 'v1', 16023, 445712, 1, 'externalUrl', 'PUBLIC');

INSERT INTO beacon_dataset_table (name, description, assemblyId, createDateTime, updateDateTime, version, variantCount, callCount, sampleCount, externalUrl, accessType) VALUES ('DATASET2', 'example dataset number 2', 'GRCh38', 'v1', 20952, 1206928, 1, 'externalUrl', 'PUBLIC');
```


One can also fill the `genomes` table using the `load_data_table()` function as well. This function
will fill in the `id` automatically so then you shouldn't use a file where you have added the `id` numbers.
For example `dataset1.csv`. Import raises error on empty cell.

```python
from beacon_api.utils.models import load_data_table

load_data_table('data/dataset1.csv')
load_data_table('data/dataset2.csv')
load_data_table('data/dataset3.csv')
```

## Using the application

The API has two endpoints, the info endpoint `/` and the query end point `/query`. The info end point
gives the user general info about the Beacon and it's datasets, while the query end point

### Info endpoint

Request:
- URL: `/`
- HTTP method: `GET`
- Parameters: `None`

Response:
- Content-type:`application/json`
- Payload: `Beacon object`

#### Examples
An example `GET` request and response to the info endpoint:

```
$ curl -v 'http://localhost:8080'
```

```
* Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to http://localhost (127.0.0.1) port 8080 (#0)
> GET / HTTP/1.1
> Host: http://localhost
> User-Agent: curl/7.54.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: gunicorn/19.9.0
< Date: Tue, 31 Jul 2018 12:10:53 GMT
< Content-Type: application/json
< Content-Length: 2391
< Set-Cookie: eeadd1720fcd75b91205443a24cfbacf=97f5c3f4c5d9d73de00e92277c49a74f; path=/; HttpOnly
< Cache-control: private
<
{
    "id": "ega-beacon",
    "name": "EGA Beacon",
    "apiVersion": "1.0.0",
    "organization": {
        "id": "EGA",
        "name": "European Genome-Phenome Archive (EGA)",
        "description": "The European Genome-phenome Archive (EGA) is a service for permanent archiving and sharing of all types of personally identifiable genetic and phenotypic data resulting from biomedical research projects.",
        "address": "",
        "welcomeUrl": "https://ega-archive.org/",
        "contactUrl": "mailto:beacon.ega@crg.eu",
        "logoUrl": "https://ega-archive.org/images/logo.png",
        "info": null
    },
    "description": "This <a href=\"http://ga4gh.org/#/beacon\">Beacon</a> is based on the GA4GH Beacon <a href=\"https://github.com/ga4gh/beacon-team/blob/develop/src/main/resources/avro/beacon.avdl\">API 0.4</a>",
    "version": "v1",
    "welcomeUrl": "https://ega-archive.org/beacon_web/",
    "alternativeUrl": "https://ega-archive.org/beacon_web/",
    "createDateTime": "2018-07-25T00:00.000Z",
    "updateDateTime": null,
    "dataset": [
        {
            "id": 1,
            "name": "DATASET1",
            "description": "example dataset number 1",
            "assemblyId": "GRCh38",
            "createDateTime": null,
            "updateDateTime": null,
            "version": null,
            "variantCount": 6966,
            "callCount": 360576,
            "sampleCount": 1,
            "externalUrl": null,
            "info": {
                "accessType": "PUBLIC"
            }
        },
        {
            "id": 3,
            "name": "DATASET3",
            "description": "example dataset number 3",
            "assemblyId": "GRCh38",
            "createDateTime": null,
            "updateDateTime": null,
            "version": null,
            "variantCount": 20952,
            "callCount": 1206928,
            "sampleCount": 1,
            "externalUrl": null,
            "info": {
                "accessType": "PUBLIC"
            }
        },
        {
            "id": 2,
            "name": "DATASET2",
            "description": "example dataset number 2",
            "assemblyId": "GRCh38",
            "createDateTime": null,
            "updateDateTime": null,
            "version": null,
            "variantCount": 16023,
            "callCount": 445712,
            "sampleCount": 1,
            "externalUrl": null,
            "info": {
                "accessType": "REGISTERED"
            }
        }
    ],
    "sampleAlleleRequests": [
        {
            "alternateBases": "A",
            "referenceBases": "C",
            "referenceName": "17",
            "start": 6689,
            "assemblyId": "GRCh37",
            "datasetIds": null,
            "includeDatasetResponses": false
        },
        {
            "alternateBases": "G",
            "referenceBases": "A",
            "referenceName": "1",
            "start": 14929,
            "assemblyId": "GRCh37",
            "datasetIds": [
                "EGAD00000000028"
            ],
            "includeDatasetResponses": "ALL"
        },
        {
            "alternateBases": "CCCCT",
            "referenceBases": "C",
            "referenceName": "1",
            "start": 866510,
            "assemblyId": "GRCh37",
            "datasetIds": [
                "EGAD00001000740",
                "EGAD00001000741"
            ],
            "includeDatasetResponses": "HIT"
        }
    ],
    "info": {
        "size": ""
    }
}
* Connection #0 to host http://localhost left intact
```


Example of how to use the GET method in the `/query` endpoint:

```
$ curl -v 'http://localhost:8080/query?referenceName=1&start=2947892&referenceBases=A&alternateBases=G&variantType=SNP&assemblyId=GRCh37&includeDatasetResponses=ALL'
```

```
* Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to http://localhost (127.0.0.1) port 8080 (#0)
> GET /query?referenceName=1&start=2947892&referenceBases=A&alternateBases=G&variantType=SNP&assemblyId=GRCh37&includeDatasetResponses=ALL HTTP/1.1
> Host: http://localhost
> User-Agent: curl/7.54.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: gunicorn/19.9.0
< Date: Tue, 31 Jul 2018 12:14:49 GMT
< Content-Type: application/json
< Content-Length: 828
< Set-Cookie: eeadd1720fcd75b91205443a24cfbacf=97f5c3f4c5d9d73de00e92277c49a74f; path=/; HttpOnly
< Cache-control: private
<
{
    "beaconId": "ega-beacon",
    "apiVersion": "1.0.0",
    "exists": true,
    "error": null,
    "allelRequest": {
        "referenceName": "1",
        "start": 2947892,
        "startMin": 0,
        "startMax": 0,
        "end": 0,
        "endMin": 0,
        "endMax": 0,
        "referenceBases": "A",
        "alternateBases": "G",
        "variantType": "SNP",
        "assemblyId": "GRCh37",
        "datasetIds": [],
        "includeDatasetResponses": "ALL"
    },
    "datasetAllelResponses": [
        {
            "datasetId": "DATASET1",
            "exists": true,
            "frequency": 0.0081869,
            "variantCount": 41,
            "callCount": 5008,
            "sampleCount": 2504,
            "note": "example dataset number 1",
            "externalUrl": null,
            "info": {
                "accessType": "PUBLIC"
            },
            "error": null
        },
        {
            "datasetId": "DATASET3",
            "exists": false,
            "frequency": 0,
            "variantCount": 0,
            "callCount": 0,
            "sampleCount": 0,
            "note": "example dataset number 3",
            "externalUrl": null,
            "info": {
                "accessType": "PUBLIC"
            },
            "error": null
        }
    ]
}
* Connection #0 to host http://localhost left intact
```


## Further information


### Project structure

```text

```

### Testing

In order to run the unit tests and [flake8](http://flake8.pycqa.org/en/latest/) we are using [tox](https://tox.readthedocs.io):
```
$ tox
```
