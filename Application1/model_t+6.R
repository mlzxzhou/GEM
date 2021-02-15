library(RcppCNPy)
library(ggplot2)

#### Load Data ####
data <- npyLoad("data/prediction/area5/t_6/data.npy")
y <- data[, 1]
xh1 <- data[, 2:11]
xh2 <- data[, 12:16]
xl1 <- data[, 17:26]
xl2 <- data[, 27:31]
xw1 <- data[, 32:36]
xw2 <- data[, 37:46]
xg1 <- data[, 47:56]
xg2 <- data[, 57:61]


y_train = y[1:2160]
y_true = y[2161:3600]

#### Fit model and make prediction ####

### GEM ###
x_train_1 = xg1[1:2160, ]
x_train_2 = xg2[1:2160, ]
x_train = cbind(x_train_1, x_train_2)
fit_g = lm(log(y_train)~x_train)
coef_0 = fit_g$coefficients[1]
coef = t(t(fit_g$coefficients[2:16]))
x_test_1 = xg1[2161:3600, ]
x_test_2 = xg2[2161:3600, ]
x_test = cbind(x_test_1, x_test_2)
y_pred_g = x_test %*% coef + coef_0

y_true = y[2161:3600]
print("t+60 All time RMSE of GEM:")
sqrt(mean((y_pred_g - log(y_true))^2)) #RMSE
print("t+60 All time MAPE of GEM:")
mean(abs(exp(y_pred_g) - y_true) / y_true) #MAPE

# peak hours #
y_two = matrix(0, 120, 2)
for (i in 1:10){
    for (j in 1:12){
        y_two[(i - 1) * 12 + j, 1] = y_pred_g[(i - 1) * 144 + 108 + j]
        y_two[(i - 1) * 12 + j, 2] = y_true[(i - 1) * 144 + 108 + j]
    }
}
print("t+60 Peak hour RMSE of GEM:")
sqrt(mean((y_two[, 1] - log(y_two[, 2]))^2))
print("t+60 Peak hour MAPE of GEM:")
mean(abs(exp(y_two[, 1])-y_two[, 2]) / y_two[, 2])


### Hellinger Distance ###
x_train_1 = xh1[1:2160, ]
x_train_2 = xh2[1:2160, ]
x_train = cbind(x_train_1, x_train_2)
fit_h = lm(log(y_train)~x_train)
coef_0 = fit_h$coefficients[1]
coef = t(t(fit_h$coefficients[2:16]))
x_test_1 = xh1[2161:3600, ]
x_test_2 = xh2[2161:3600, ]
x_test = cbind(x_test_1, x_test_2)
y_pred_h = x_test %*% coef + coef_0

y_true = y[2161:3600]
print("t+60 All time hour RMSE of Hellinger:")
sqrt(mean((y_pred_h - log(y_true))^2)) #RMSE
print("t+60 All time MAPE of Hellinger:")
mean(abs(exp(y_pred_h) - y_true) / y_true) #MAPE

# peak hours #
y_two = matrix(0,120,2)
for (i in 1:10){
    for (j in 1:12){
        y_two[(i - 1) * 12 + j, 1] = y_pred_h[(i - 1) * 144 + 108 + j]
        y_two[(i - 1) * 12 + j, 2] = y_true[(i - 1) * 144 + 108 + j]
    }
}

print("t+60 Peak hour RMSE of Hellinger:")
sqrt(mean((y_two[, 1] - log(y_two[, 2]))^2))
print("t+60 Peak hour MAPE of Hellinger:")
mean(abs(exp(y_two[, 1]) - y_two[, 2])/y_two[, 2])


### L2 Distance ###
x_train_1 = xl1[1:2160, ]
x_train_2 = xl2[1:2160, ]
x_train = cbind(x_train_1, x_train_2)
fit_l = lm(log(y_train)~x_train)
coef_0 = fit_l$coefficients[1]
coef = t(t(fit_l$coefficients[2:16]))
x_test_1 = xl1[2161:3600, ]
x_test_2 = xl2[2161:3600, ]
x_test = cbind(x_test_1, x_test_2)
y_pred_l = x_test %*% coef + coef_0

y_true = y[2161:3600]
print("t+60 All time hour RMSE of L2:")
sqrt(mean((y_pred_l - log(y_true))^2)) #RMSE
print("t+60 All time MAPE of L2:")
mean(abs(exp(y_pred_l) - y_true) / y_true) #MAPE

# peak hours #
y_two = matrix(0, 120, 2)
for (i in 1:10){
    for (j in 1:12){
        y_two[(i - 1) * 12 + j, 1] = y_pred_l[(i - 1) * 144 + 108 + j]
        y_two[(i - 1) * 12 + j, 2] = y_true[(i - 1) * 144 + 108 + j]
    }
}
print("t+60 Peak hour RMSE of L2:")
sqrt(mean((y_two[, 1] - log(y_two[, 2]))^2))
print("t+60 Peak hour MAPE of L2:")
mean(abs(exp(y_two[, 1]) - y_two[, 2]) / y_two[, 2])


### Wasserstein Distance ###
x_train_1 = xw1[1:2160, ]
x_train_2 = xw2[1:2160, ]
x_train = cbind(x_train_1, x_train_2)
fit_w = lm(log(y_train)~x_train)
coef_0 = fit_w$coefficients[1]
coef = t(t(fit_w$coefficients[2:16]))
x_test_1 = xw1[2161:3600, ]
x_test_2 = xw2[2161:3600, ]
x_test = cbind(x_test_1, x_test_2)
y_pred_w = x_test %*% coef + coef_0

y_true = y[2161:3600]
print("t+60 All time hour RMSE of Wasserstein:")
sqrt(mean((y_pred_w - log(y_true))^2)) #RMSE
print("t+60 All time MAPE of Wasserstein:")
mean(abs(exp(y_pred_w) - y_true) / y_true) #MAPE


# peak hours #
y_two = matrix(0,120,2)
for (i in 1:10){
    for (j in 1:12){
        y_two[(i - 1) * 12 + j, 1] = y_pred_w[(i - 1) * 144 + 108 + j]
        y_two[(i - 1) * 12 + j, 2] = y_true[(i - 1) * 144 + 108 + j]
    }
}
print("t+60 Peak hour RMSE of Wasserstein:")
sqrt(mean((y_two[, 1] - log(y_two[, 2]))^2))
print("t+60 Peak hour MAPE of Wasserstein:")
mean(abs(exp(y_two[, 1]) - y_two[, 2])/y_two[, 2])

#### Make Figure 5(a) ####
xdata <- 1:1008

### Plot of L2 distance ###
plot(xdata, y_true[433:1440], type = "l", col = "blue", pch = "o", lty = 1, ylim = c(0.3, 1),xlab = 'Time Index',ylab = 'Answer Rate')
par(new=TRUE)
plot(xdata, exp(y_pred_l[433:1440]), type = "l", col = "pink", pch = "o", lty = 1, ylim = c(0.3,1), xlab = 'Time Index', ylab = 'Answer Rate')
abline(v = 144, col = "black", lwd = 1, lty = 2)
abline(v = 288, col = "black", lwd = 1, lty = 2)
abline(v = 432, col = "black", lwd = 1, lty = 2)
abline(v = 576, col = "black", lwd = 1, lty = 2)
abline(v = 720, col = "black", lwd = 1, lty = 2)
abline(v = 864, col = "black", lwd = 1, lty = 2)

### Plot of Hellinger distance ###
plot(xdata, y_true[433:1440], type = "l", col = "blue", pch = "o", lty = 1, ylim = c(0.3, 1), xlab = 'Time Index', ylab = 'Answer Rate')
par(new = TRUE)
plot(xdata, exp(y_pred_h[433:1440]), type = "l", col = "goldenrod", pch = "o", lty = 1, ylim = c(0.3, 1), xlab = 'Time Index', ylab = 'Answer Rate')
abline(v = 144, col = "black", lwd = 1, lty = 2)
abline(v = 288, col = "black", lwd = 1, lty = 2)
abline(v = 432, col = "black", lwd = 1, lty = 2)
abline(v = 576, col = "black", lwd = 1, lty = 2)
abline(v = 720, col = "black", lwd = 1, lty = 2)
abline(v = 864, col = "black", lwd = 1, lty = 2)

### Plot of Wasserstein distance ###
plot(xdata, y_true[433:1440], type = "l", col = "blue", pch = "o", lty = 1, ylim = c(0.3, 1), xlab = 'Time Index', ylab = 'Answer Rate')
par(new = TRUE)
plot(xdata, exp(y_pred_w[433:1440]), type = "l", col = "green", pch = "o", lty = 1, ylim = c(0.3,1), xlab = 'Time Index', ylab = 'Answer Rate')
abline(v = 144, col = "black", lwd = 1, lty = 2)
abline(v = 288, col = "black", lwd = 1, lty = 2)
abline(v = 432, col = "black", lwd = 1, lty = 2)
abline(v = 576, col = "black", lwd = 1, lty = 2)
abline(v = 720, col = "black", lwd = 1, lty = 2)
abline(v = 864, col = "black", lwd = 1, lty = 2)
### Plot of GEM ###
plot(xdata, y_true[433:1440], type = "l", col = "blue", pch = "o", lty = 1, ylim = c(0.3, 1), xlab = 'Time Index', ylab = 'Answer Rate')
par(new = TRUE)
plot(xdata, exp(y_pred_g[433:1440]), type = "l", col = "red", pch = "o", lty = 1, ylim = c(0.3,1),xlab = 'Time Index', ylab = 'Answer Rate')
abline(v = 144, col = "black", lwd = 1, lty = 2)
abline(v = 288, col = "black", lwd = 1, lty = 2)
abline(v = 432, col = "black", lwd = 1, lty = 2)
abline(v = 576, col = "black", lwd = 1, lty = 2)
abline(v = 720, col = "black", lwd = 1, lty = 2)
abline(v = 864, col = "black", lwd = 1, lty = 2)

#### Make Figure 5(b) ####

S_h = (y_pred_h - log(y_true))^2
S_hi = matrix(S_h[433:1440], 144, 7)
mS_hi = sqrt(colMeans(S_hi))
#tmp41 = sqrt(rowMeans(matrix(tmp3,7,3)))

S_w = (y_pred_w - log(y_true))^2
S_wi = matrix(S_w[433:1440], 144, 7)
mS_wi = sqrt(colMeans(S_wi))


S_g = (y_pred_g-log(y_true))^2
S_gi = matrix(S_g[433:1440], 144, 7)
mS_wi = sqrt(colMeans(S_gi))

RMSE = c(mS_hi,mS_wi,mS_wi)


metric_index = rep(c("Hellinger Distance", "Wasserstein Distance",
                     "Spatial Coherence Metric"), each=7)
day_index = rep(c('Tuesday', 'Wednesday', 'Thursday', 'Friday',
                  'Saturday', 'Sunday', 'Monday'), 3)

data = data.frame(metric_index, day_index, RMSE)

level.order = c('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
level.metric = c("Hellinger Distance", "Wasserstein Distance", "Spatial Coherence Metric")

data$day_index <- factor(data$day_index, levels = level.order)
data$metric_index <- factor(data$metric_index, levels = level.metric)

ggplot(data, aes(x = day_index, y = RMSE, fill = metric_index)) + geom_bar(position = "dodge", stat = "identity") + theme(legend.position = "top")
