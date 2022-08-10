# Summary

The full US intersection inventory data processing pipeline runs on Databricks integrated with AWS S3. Databricks provides a user friendly interface to perform the necessary distributed computing workload to ingest, extract, and characterize intersections for the entire US. The code is organized into notebooks that can be imported into the Databricks workspace. Details on specific notebook functions are given below.

# Setting up initial Databricks cluster
This ReadMe assumes that you have an active AWS account. If you do not, refer to [Amazon's documentation](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).
It also assumes you have a Databricks account with permissions to create a workspace and cluster; if you do not, please refer to their [setup guide](https://docs.databricks.com/getting-started/account-setup.html).  

### Amazon S3 Setup
From the Management Console, navigate to S3, then select "Create Bucket". Name it as you please and continue; the default options are fine.

* Create a folder called input_data. In it, drop the us-county-boundaries geojson.
* Create a folder under input_data called usa. Under this folder create one called osm, a final folder called states under that. (Alternatively, set up the data as you please and change the notebooks later to point to your new structure).
* Under input_data/usa/osm/states, place the osm files you wish to ingest. Each file should end in the suffix `-latest.osm.pbf`.
  * You can find the latest OSM files on the [Geofabrik server](https://download.geofabrik.de/north-america/us.html).
  * An example python script to automatically download the files to your S3 bucket is available in the databricks/example_files directory. 

#### Creating AWS Credentials for Databricks
* From the Management Console, navigate to IAM, then select "Users" followed by "Add users". 
* Name it whatever you want and tick "Access key - Programmatic access". Leave "Password - AWS Management Console access" unchecked. Click next and proceed to permissions.
* Give it the AmazonS3FullAccess policy. Click next.
* (Optional) Give it tags if you want and click next.
* Click Create User
* Copy your Access Key ID and Secret Access key and store them somewhere safe. You'll need these later on.

### Databricks Setup

#### Creating a Workspace
Create a workspace by selecting Workspaces from the sidebar, then Create workspace -> Quickstart. 
Enter a name, select an appropriate region, and link it to S3.
From the workspaces page, select the workspace matching the name, and click "Open Workspace".

#### Creating a Cluster
In your workspace, select "Compute" from the sidebar, then "Create Cluster".

Under the Configuration tab, set the following options:
* Standard Cluster mode
* Databricks Runtime Version **10.4 LTS (includes Apache Spark 3.2.1, Scala 2.12)**.
* Enable autoscaling 
* We used  m4.large worker / driver, with 8 GB Memory and 2 cores. Autoscaling was set between 1 and 32 max workers for this phase of the project.

Under the Libraries tab, import the following Maven libraries:
* com.acervera.osm4scala:osm4scala-spark3-shaded_2.12:1.0.7
* org.apache.sedona:sedona-sql-3.0_2.12:1.2.0-incubating
* org.apache.sedona:sedona-python-adapter-3.0_2.12:1.2.0-incubating
* org.apache.sedona:sedona-core-3.0_2.12:1.2.0-incubating
* org.datasyslab:geotools-wrapper:1.1.0-25.2
* commons-httpclient:commons-httpclient:20020423

You will also need Spark SQL, Spark Core and Elasticsearch Spark. I found that accessing them through Maven on Databricks did not work, but had success uploading the jars directly through the drag and drop interface. They are included in this repo under the databricks/prereq_jars folder. You will want:
* spark-sql_2.12-3.2.1
* spark-core_2.12-3.2.1
* elasticsearch-spark-30_2.12-8.2.2

Finally, install the following through PyPI:
* apache-sedona
* jts
* ndjson
* elasticsearch<7.14.0

# Importing Notebooks into Databricks

In order to upload a notebook from this repository to databricks, from the workspace sidebar right click in the area you want to import the notebook to, click Import, and select the desired notebook(s).

# Setup and Mount
Under databricks/notebooks/"1 -  Setup and Initial Ingestion", import and run the One-timeSetup notebook then import the Mount Notebook. Open the Mount notebook and input your access keys, bucket name, and mount name in the appropriate fields before running it.
* One-Time Setup creates a shared schema for useful things that don't correspond to any region, including tables to help feature types conform to MIRE standards and angle processing functions.
* "Mount" mounts the S3 bucket and makes the data there accessible. 

# Ingestion and Processing
Under databricks/notebooks/"2 - Ingestion and Processing", import all notebooks, then run the RegionIngestionControlLoop. The control loop will call the other two notebooks on each region in the target directory.
* Generic Region does the bulk of the work and creates the schema, loads the osm data from the mount, and creates and populates all tables.
* Midblock Crossing does a single comparatively expensive operation; it creates a spatial RDD and identifies midblock crossings using the heuristic "footway crossing road with no road/road intersection within 50 meters".

### If the loop crashes
Everything doesn't always go right. The control loop logs its work as it goes, and processes regions alphabetically. 
* Check the output for the last region successfully processed
* Add that region and all alphabetically prior regions to the blacklist by uncommenting them
* Rerun the loop

### If the loop still crashes
* Make a note of the region it is crashing on
* Uncomment that region
* Rerun the loop
* Debug the crashing region separately

# Exporting database to ElasticSearch

In order to export the newly minted datasets into a user-friendly csv format, first open the ElasticSearchExport notebook under databricks/notebooks/"3 - ElasticSearch Export" and enter your Elasticsearch credentials. If you do not have them, the CASSE team at Intellibridge can provide some.
Verify that the expected index ("dot" in the phase II) and mapping exist using this shell command, replacing the API key with a valid one:

`curl -X GET -H "Authorization: ApiKey <your_API_key_here>" https://casse-dev-1.es.us-east-1.aws.found.io/dot/_mapping`

The mapping should align with the example mapping provided in databricks\example_files.

Run the notebook dot_export_control_loop to export the data to ElasticSearch.

# Exporting database to S3

In order to export the newly minted datasets into a user-friendly csv format, use the notebook Export_view_to_csv under databricks/notebooks/"4 - File Exports".
The notebook assumes the data tables have been created via previous steps, and you will need to mount a desired output location if you want the data in a different bucket than your inputs. An example is provided in the notebook.
