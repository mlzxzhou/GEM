## Requirements
    
    * Python 3
    * cvxpy


## Usage


### First run run0.sh 

    * Generate  ratio and global_metric
    * from April 21 to April 30
    * Result in ../data/putput/area5/

### Second run run1.sh

    * Generate  ratio and global_metric
    * From May 1st to May 21st
    * Result in ../data/output/area5/

### Third run functional_prepare.py

    * To generate dependent and independent variables for training and testing
    * Result in ../data/prediction/area5/

### Fourth Run model_t+1.R and model_t+6.R

    * To test the prediction effects of GEM, Hellinger Distance, L2 Distance and Wasserstein Distance