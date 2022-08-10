# Experimentation and Analysis

### case_study_modeling

This directory houses modeling of the case study locations and run instructions [here](case_study_modeling/README.md). The goal is to predict an intersections propensity for accidents based on its inherent features. It contains:
- Case_Study_Model_DC : A simple ML model for the DC area.
- Case_study_model_Iowa : A more sophisticated model using deep ML 
- Case_study_model_Iowa_with_vae : An extention to the previous model that also incorporates the output of the computer vision model. 

### computer_vision

This directory houses the work to incorporate computer vision of satellite imagery and intersection "masks" into the deep learning model. GPU is necesssary for training. 

### Future work

The model provided as a part of the phase 2 research can be used to inform intersection safety. A potential future use case would be a user interface that accepts certain intersection parameters such as traffic loads, width, number of lanes, lighting, etc. We are constrained by knowing how many legs an intersection might have or how much traffic it must hold, but we can adjust the other parameters to see how to best build future intersections, similar to: http://www.cmfclearinghouse.org/resources_selection.cfm.

