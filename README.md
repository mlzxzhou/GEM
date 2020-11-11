# GEM-Demo

### System requirement

Programming language: Python 3
    
Python Packages: cvxpy 1.1.5, numpy, scipy, pandas, sklearn


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

   
