# U.Group Logstash

This repository provides a containerized [Logstash](https://www.elastic.co/logstash/) instance.

## Section 1: Structure

This template organizes its code into two directories:

```
.
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

## Section 3: TODOs

1. Add config and pipeline templates to connect databases.
