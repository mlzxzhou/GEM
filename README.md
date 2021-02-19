# GEM

This is an implementation of the ‘Order Answer-rate Prediction’ application in Section 4.1 and the 'Policy Evaluation' application in Section 4.3 of paper '**Graph-Based Equilibrium Metrics for Dynamic Supply-Demand Systems with Applications to Ride-sourcing Platforms**'. In this repository, we skip the data processing part to avoid disclosing the raw data. All the required codes to reproduce the main results of the two applications in the paper, and a guidance document ‘README.txt’, are provided. 

### Requirement

* Python 3
    
* Python Packages: cvxpy 1.1.5, numpy, scipy, pandas, sklearn

### Dataset

The required data can be obtained from the following website after sigining in:
```
https://outreach.didichuxing.com/appEn-vue/DatasetProjectDetail?id=1026
```

The demand and supply data, named as 'area5_{}_order.npz' and 'area5_{}_driver.npz' can be found in the folder 'driver_count' and 'order_count', where the number inside the '{}' represents the date.  

Put all the supply-demand data from 20180421 to 20180521 in the path
```
Application1/data/processed/area5/
```
Put all the supply-demand data from 20181112 to 20181216 in the path
```
Application3/data/processed/area5/
```
The file 'grids_to_id.pickle' in the folder 'grids' needs to be copied to the above two paths.

File 'data_cost_lambda_eq1.csv' needs to be placed in the path
```
Application3/data/ab_test/area5/
```
All files in the folder 'AA_AB_test' should be placed in the path 
```
Application3/
``

### Compute GEM

Compute supply-demand ratio and global_metric from April 21 to April 30 for Application 1 and from Nov 12 to Nov 25 for Application 3. Result in data/output/area5/
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

