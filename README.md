# GEM

This is an implementation of the ‘Order Answer-rate Prediction’ application in Section 4.1 and the 'Policy Evaluation' application in Section 4.3 of paper '**Graph-Based Equilibrium Metrics for Dynamic Supply-Demand Systems with Applications to Ride-sourcing Platforms**'. In this repository, we skip the data processing part to avoid disclosing the raw data. All the required codes to reproduce the main results of the two applications in the paper, and a guidance document ‘README.md’, are provided. 

### Requirement

* Python 3
    
* Python Packages: cvxpy 1.1.5, numpy, scipy, pandas, sklearn

### Dataset

The required data can be obtained from the following website after sigining in:
```
https://outreach.didichuxing.com/appEn-vue/DatasetProjectDetail?id=1026
```

The demand and supply data, named as 'area5_xxxx_order'.npz and 'area5_xxxx_driver.npz' can be found in the folder 'area_driver' and 'area_order', where the number 'xxxx' represents the date.  

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
```

### Compute GEM

Compute supply-demand ratio and global_metric from 20180421 to 20180521 for Application 1. 
```
cd Application1/

# from 20180421 to 20180430
sh run0.sh

# from 20180501 to 20180521
sh run1.sh
```
After compute, you will find:
    - 'area5_xxxx_metric.npz', where the number 'xxxx' represents the date.  This file
```
Application1/data/output/area5/
```
Compute supply-demand ratio and global_metric from 20181112 to 20181216 for Application 3.
```
cd Application3/

# from 20181112 to 20181125
sh run0.sh

# from 20181203 to 20181216
sh run1.sh
```

Result in the path
```
Application3/data/output/area5/
```

### Application 1：Order Answer-rate Prediction

compute dependent and independent variables for prediction. 
```
cd Application1/

python functional_prepare.py
```
Result in the path
```
Application1/data/prediction/area5/
```
  
Test the prediction effects of GEM, Hellinger Distance, L2 Distance and Wasserstein Distance
```
cd Application1/

nohup R CMD BATCH model_t+1.R &
nohup R CMD BATCH model_t+6.R &
```

### Application 3:Policy Evaluation

compute inputs for policy evaluation. 
```
cd Application3/

python cal_out.py
```
Result in the path
```
Application3/data/ab_test/area5/
```
examine the marginal effect of policy on GEM
```
cd Application3/

python AB_test.py
```

