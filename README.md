# beacon-python
[Beacon API specifications](https://github.com/ga4gh-beacon/specification/blob/release-1.0.0/beacon.md)


## Quick start


## Configure database

### Create database

The application is using the object relational mapper (ORM) SQLAlchemy to handle much of the communication 
between the application and the database, and that is why the database tables are created using SQLAlchemy.
So instead of manually creating the Postgresql tables using `psql` in the command line, the tables are 
created by calling the `db.create_all` method that uses the `db` object from SQLAlchemy. To call the method we 
use the Python shell in the command line. 


Open the Python shell in the command line:
```Shell
$ python3
```
Create the tables:
```python
>>> from app import db
>>> db.create_all()
``` 

This will create the database tables according to the schema specified in `models.py`.

### Load data

In this example we will fill the `genomes` table first, the order you fill the tables in does not matter
because the tables does not have any direct relations. In the example we load three datasets to the database.

The table needs in the first column the `id`, witch is a number starting from one and iterates with +1 for every row.
If the datasets you are loading dont have this `id` in the first row you can add it the following way.

```Shell
$ awk '{printf "%s;%s\n", NR,$0}' dataset1.csv > dataset1_.csv
$ awk '{printf "%s;%s\n", NR+72,$0}' dataset2.csv > dataset2_.csv
$ awk '{printf "%s;%s\n", NR+161,$0}' dataset3.csv > dataset3_.csv
```

The table column `dataset_id` is the name of the table. If the file that you are loading doesent have the right name in 
that column you can change it using:

```Shell
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET1”;print $0}' dataset1_.csv > set1.csv
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET2”;print $0}' dataset2_.csv > set2.csv
$ awk -F';' 'BEGIN{OFS=";"}{$2="DATASET3”;print $0}' dataset3_.csv > set3.csv
```

Then we load the `genomes` table with the files. Open `psql` in the command line:

```Shell
$ psql beacondb
```
Copy the files into the table:

```SQL
beacondb=# COPY genomes FROM '/opt/app-root/files/set1.csv' DELIMITER ';' CSV;
beacondb=# COPY genomes FROM '/opt/app-root/files/set2.csv' DELIMITER ';' CSV;
beacondb=# COPY genomes FROM '/opt/app-root/files/set3.csv' DELIMITER ';' CSV;
```

Then we check for the right values to fill in the beacon_dataset_table in the variantCount and callCount:

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
from models import load_dataset_table

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


You can also fill the `genomes` table using the `load_data_table()` function aswell. This function 
will fill in the `id` automatically so then you shouldn't use a file where you have added the `id` numbers.

```python
from models import load_data_table

load_data_table('set1.csv')
load_data_table('set2.csv')
load_data_table('set3.csv')
```

## Using the application

The API has two endpoints, the info endpoint `/` and the query end point `/query`. The info end point 
gives the user general info about the Beacon and it's datasets, while the query end point 

### Info endpoint

#### Request 
###### - URL: `/`
###### - HTTP method: `GET`
###### - Parameters: `None`

#### Response
###### Content-type:`application/json`
###### Payload: `Beacon object`

#### Examples 
An example `GET` request and response to the info endpoint:

```Shell
$ curl -v 'http://beaconapi-elixirbeacon.rahtiapp.fi/'
```

```Shell
*   Trying 193.167.189.101...
* TCP_NODELAY set
* Connected to beaconapi-elixirbeacon.rahtiapp.fi (193.167.189.101) port 80 (#0)
> GET / HTTP/1.1
> Host: beaconapi-elixirbeacon.rahtiapp.fi
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
* Connection #0 to host beaconapi-elixirbeacon.rahtiapp.fi left intact
```

### Query endpoint

#### Request
###### - URL: `/query`
###### - HTTP method: `GET`, `POST`
###### - Content-Type: `application/x-www-form-urlencoded`(POST)
###### - Parameters: `BeaconAlleleRequest`

#### Response
###### Content-type:`application/json`
###### Payload: `Beacon Allele Response object`


#### Examples

Example of how to use the GET method in the `/query` endpoint:

```Shell
$ curl -v 'http://beaconapi-elixirbeacon.rahtiapp.fi/query?referenceName=1&start=2947892&referenceBases=A&alternateBases=G&variantType=SNP&assemblyId=GRCh37&includeDatasetResponses=ALL'
```
    
    
```Shell
*   Trying 193.167.189.101...
* TCP_NODELAY set
* Connected to beaconapi-elixirbeacon.rahtiapp.fi (193.167.189.101) port 80 (#0)
> GET /query?referenceName=1&start=2947892&referenceBases=A&alternateBases=G&variantType=SNP&assemblyId=GRCh37&includeDatasetResponses=ALL HTTP/1.1
> Host: beaconapi-elixirbeacon.rahtiapp.fi
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
* Connection #0 to host beaconapi-elixirbeacon.rahtiapp.fi left intact
```


## Further information


### Project structure

```text
beacon-python
├─beacon_api
|   ├─beacon_info.py
|   ├─check_functions.py
|   ├─error_handelers.py
|   ├─models.py
|   ├─requirements.txt
|   └─wsgi.py
└─test
    ├─test-expected_outcome-py
    ├─test_get_200.py
    ├─test_get_400.py
    ├─test_get_401.py
    ├─test_post_200.py
    ├─test_post_400.py
    └─test_post_401.py
```
