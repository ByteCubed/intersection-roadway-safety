# U.Group Elasticsearch Template

This repository provides a containerized Elasticsearch instance.

## Section 1: Structure

This template organizes its code into two directories:

```
.
├── data    # data storage
└── devsecops  # deployment code for template services
    └── local  # folder for local deployment
        └── docker-compose.yml   # docker compose deployment script
```

## Section 2: Starting and Stopping (Locally)

To build and start the services in this template:

1. Open a command line interface session.
2. Change directories to the folder that contains this [README](README.md) file.
3. Run this command:
    ```
    docker-compose -f devsecops/local/docker-compose.yml up --force-recreate --build
    ```

To stop the services in this template:

1. Open a command line interface session.
1. Change directories to the folder that contains this [README](README.md) file.
1. Run this command:
    ```
    docker-compose -f devops/local/docker-compose.yml down
    ```

## Section 3: Starting and Stopping (AWS RDS)

Talk to Jeff!

## Section 4: Accessing (Locally)

To access this service from your **local machine** (like from a REST
client), use these connection settings:

* **Host**: `localhost`
* **Port**: `9200`
* **Username**: `elastic`
* **Password**: see [root.env](devsecops/local/env/root.env) file

To access this service from **other Docker services in this Docker network**, use these connection settings:

* **Host**: `ug-elasticsearch`
* **Port**: `9200`
* **Username**: `elastic`
* **Password**: see [root.env](devsecops/local/env/root.env) file

## Section 5: Notes

To reinstall your Elasticsearch instance locally (wiping out all existing data and triggering the init scripts to run again):

1. Stop the Docker containers per section 2.
2. Run this command to remove the volume:
    ```
    docker volume rm local_ug-elasticsearch
    ```
3. Restart the Docker containers per section 2.
    1. This will rebuild the Elasticsearch instance from script.
