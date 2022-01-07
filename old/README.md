# dot-road-safety

Experiments, proof-of-concepts, and demonstrations for DOT work. 


## Preparing Data

Data processing piplines are managed by DVC.

`pip install dvc`

Data files are stored in our s3 bucket s3://dot-roadway-safety. You must configure your AWS access keys to be able to access this bucket.

Add the s3 remote to configure dvc:

`dvc remote add dotdata s3://dot-roadway-safety`

To get all the latest data, run `dvc pull`. 

In the `data/` directory, run `dvc repro` to recreate all the data processing pipelines.
