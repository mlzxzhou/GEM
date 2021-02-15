# Graph-Based Equilibrium Metrics for Dynamic Supply-Demand Systems with Applications to Ride-sourcing Platforms

This is a demo to reproduce the ‘Answer-rate Prediction’ application in Section 4.1 and Section 4.3 of paper '**Graph-Based Equilibrium Metrics for Dynamic Supply-Demand Systems with Applications to Ride-sourcing Platforms**'. In this repository, we skip the data processing part to avoid disclosing the pattern of the raw data. All the required files to run the simulation including codes, simulated data, some tool boxes, and a guidance document ‘README.txt’, are all provided in the folder ‘application1’ and ‘application3’. 

### System requirement

* Programming language: Python 3
    
* Python Packages: cvxpy 1.1.5, numpy, scipy, pandas, sklearn

### dataset

All data can be obtained from the following website:
```
https://outreach.didichuxing.com/app-vue/DatasetProjectDetail?id=1025
```
The data in AA_AB_test can be placed directly under the Application3 folder.

The files in area_driver and area_order need to be divided by time.

Place the data from April to May 2018 in
```
Application1/data/processed/area5/
```
Place the data from November to December 2018 in
```
Application3/data/processed/area5/
```
The grids_to_id.pickle in grids needs to be copied to the location of the above two folders.

data_cost_lambda_eq1.csv in grids needs to be placed in the 
```
Application3/data/ab_test/area5/
```

### Preprocess data

Generate ratio and global_metric from April 21 to April 30 in Application 1 and from Nov 12 to Nov 25 in Application 3. Result in data/output/area5/
```
sh run0.sh
```

Generate ratio and global_metric from May 1st to May 21st in Application 1 and from Dec 3 to Dec 17 in Application 3 . Result in data/output/area5/
```
sh run1.sh
```

### Testing and prediction in Application 1

Generate dependent and independent variables for training and testing. Result in data/prediction/area5/
```
python functional_prepare.py
```
  
Test the prediction effects of GEM, Hellinger Distance, L2 Distance and Wasserstein Distance
```
nohup R CMD BATCH model_t+1.R &
nohup R CMD BATCH model_t+6.R &
```

### AB test in Application 3

Generate input for AB test. Result in data/ab_test/area5/
```
python cal_out.py
```

AA/AB test
```
python AB_test.py
```

