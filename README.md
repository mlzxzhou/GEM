# GEM-Demo

This is a demo to reproduce the ‘Answer-rate Prediction’ application in Section 4.1 of paper '**Graph-Based Equilibrium Metrics for Dynamic Supply-Demand Systems with Applications to Ride-sourcing Platforms**'. Note that since all the demand and supply data is simulated, the prediction results obtained by running this demo may not be exactly the same with those reported in the paper. In this demo, we skip the data processing part to avoid disclosing the pattern of the raw data. All the required files to run the simulation including codes, simulated data, some tool boxes, and a guidance document ‘README.txt’, are all provided in the folder ‘demo’. 

### System requirement

* Programming language: Python 3
    
* Python Packages: cvxpy 1.1.5, numpy, scipy, pandas, sklearn


### Preprocess data

Generate ratio and global_metric from April 21 to April 30. Result in demo/data/output/area5/
```
sh run0.sh
```

Generate ratio and global_metric from May 1st to May 21st. Result in demo/data/output/area5/
```
sh run1.sh
```

### Testing and prediction

Generate dependent and independent variables for training and testing. Result in demo/data/prediction/area5/
```
python functional_prepare.py
```
  
Test the prediction effects of GEM, Hellinger Distance, L2 Distance and Wasserstein Distance
```
nohup R CMD BATCH model_t+1.R &
nohup R CMD BATCH model_t+6.R &
```

   
