# Department of Transportation: Roadway Safety: Local

This directory creates a local environment for running services of the Department of Transportation's Roadway Safety: Phase II project.

## Section 1: Structure

This template organizes its code into one directory:

1. **[ug-postgresql](data/ug-postgresql)**: data folder for PostgreSQL service.

## Section 2: Starting and Stopping (Locally)

To build and start the services in this template, including populating the database and retriggering data ingestion:

1. Open a command line interface session.
2. Change directories to the folder that contains this [README](README.md) file.
3. Run this command:
    ```
    docker-compose up --force-recreate --build
    ```

To stop the services in this template:

1. Open a command line interface session.
1. Change directories to the folder that contains this [README](README.md) file.
1. Run this command:
    ```
    docker-compose down
    ```

## Section 3: Accessing (Locally)

To access this service from your **local machine** (like from a SQL
client), use these connection settings:

* **Host**: `localhost`
* **Port**: `5433`
* **Database**: `rws`
* **Username**: `ug_username`
* **Password**: `ug_password`

To access this service from **other Docker services in this Docker network**, use these connection settings:

* **Host**: `ug-postgresql`
* **Port**: `5432`
* **Database**: `rws`
* **Username**: `ug_username`
* **Password**: `ug_password`

## Section 4: Notes

To reinstall your PostgreSQL database locally (wiping out all existing data and triggering the init scripts to run again):

1. Stop the Docker containers per section 2.
2. Run this command to remove the volume:
    ```
    docker volume rm local_ug-postgresql  
    ```
3. Restart the Docker containers per section 2.
    1. This will rebuild the PostgreSQL database from script. By default, the
    database will rebuild with the users, schema, and structures in the
    [`data/ug-postgresql/init`](data/ug-postgresql/init) directory.
