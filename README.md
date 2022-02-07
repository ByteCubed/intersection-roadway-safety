# Department of Transportation: Roadway Safety

This repository contains services for instantiating Roadway Safety services. It contains application data, data, and deployment code for key services. The project's microservices architecture allows services to be captured in separate folders and will be independently deployable, both locally and in the cloud. For a complete overview, see the [documentation](documentation) folder's [technical overview](technical_overview.docx).

![](documentation/overview.png)

If you have trouble reading this document, paste its contents into an online Markdown editor like [Dillinger](https://www.dillinger.io/).

## Section 1: Overview

The repository is divided into four sections:

```
.
├── data                        # Data for services
├── devsecops                   # Deployment code for services
│   └── local                   # Local deployment code
├── documentation               # Human-readable project documentation
│   └── Technical Overview.docx # High-level technical overview
└── services                    # Application  code for services
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
2. Change directories to the folder that contains this [README](README.md) file.
3. Run this command:
    ```
    docker-compose -f devsecops/local/docker-compose.yml down -v
    ```
    * NOTE: The `-v` flag will remove all persistent data.

## Section 3: TODOs (Incomplete)

1. Standardize OSM devsecops practices, including deployment documentation.
2. Incorporate Logstash to accelerate data pipelines.
3. Develop cloud deployment standards.
4. Incorporate DVC.
5. Incorporate existing Mapbox data ingestion processes.
6. Incorporate extra crash data sources.
7. Enable data science analyses.
8. Extend CASSE/visualization capability.
