This service will ingest the data that has been processed for the two case study locations (DC and Iowa) for the purpose of statistical modeling of intersections given the features that have been collected thus far. 

To use:

1. Make sure the local postgres database has been successfully populated by executing the 'docker compose' instructions in the root folder of this repo. 
2. From this directory execute: 'pip install -r requirements.txt'
3. Execute 'jupyter-notebook'
4. If the browser window does not automatically load the jupyter server, use a browser to navigate to localhost:8889/tree, or whichever port the server is accessibly on.
5. Select Case_Study_Deep_Learning_DC(Iowa).ipynb from the jupyter interface, and run all cells.

Output:
	- The notebooks will produce flat csv files that may be interfaced with any sort of dashboard or analytics software.
	- Each notebook will also estimate the model eficacy and estimate uncertainties of predictions
	- Each notebook will save a trained model in pkl format.

Model Architecture:
	- The current machine learning model uses a deep nerual network  with a single output layer that uses a linear activation function.

Todo:
	- Set the notebooks up to also use dvc to store input data, store models, and run pipeline.
