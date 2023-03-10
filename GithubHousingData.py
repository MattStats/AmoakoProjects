#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 15:29:31 2023

@author: Matthew
"""
#Dataset link: https://www.kaggle.com/datasets/shibumohapatra/house-price

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp

cal = pd.read_csv('1553768847-housing.csv')
cal.dropna(axis = 0, inplace=True)
#The median_house_value cutoff occurs at $500001. This project serves to predict 
# median house prices for the common man
cal2 = cal[cal['median_house_value'] <= 500000].copy()

#Bedrooms, total rooms, and population per household were variables that we wanted
# to test in our model
cal2['bedroomhold'] = cal2['total_bedrooms']/ cal2['households']
cal2['roomhold'] = cal2['total_rooms']/ cal2['households']
cal2['pophold'] = cal2['population']/ cal2['households']

# Outliers from these variables were taken out of the data set to reflect the 
# project goal of prediction median house values for the common man
bedcutoff = cal2['bedroomhold'].mean() + (3 * cal2['bedroomhold'].std())
roomcutoff = cal2['roomhold'].mean() + (3 * cal2['roomhold'].std())
popcutoff = cal2['pophold'].mean() + (3 * cal2['pophold'].std())

cal3 = cal2[(cal2['bedroomhold'] <= bedcutoff) & (cal2['roomhold'] <= roomcutoff) &
(cal2['pophold'] <= popcutoff)].copy()


#Remove unnecessary columns
drop_columns = 'total_rooms total_bedrooms population households'.split()
cal3.drop(drop_columns, axis =1, inplace = True)


from sklearn.model_selection import train_test_split
categorical = pd.get_dummies(cal3, columns = ['ocean_proximity'])

categorical['ocean_proximity_NEARBAY'] = categorical['ocean_proximity_NEAR BAY']
categorical['ocean_proximity_NEAROCEAN'] = categorical['ocean_proximity_NEAR OCEAN']
predictors = categorical.drop('median_house_value', axis =1)
response = cal3['median_house_value']
x_train, x_test, y_train, y_test = train_test_split(predictors,response, test_size =0.3, random_state =101)
cal4 = pd.concat([x_train,y_train], axis =1)


#Perform Linear Regression Using Training Data
from statsmodels.formula.api import ols
regress = ols('y_train ~ x_train',data = cal4).fit()
print('House_Regress Summary')
print("\n")
print(regress.summary())

# Detecting Multicolinearity with VIF
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif_data = pd.DataFrame()
vif_data["feature"] = x_train.columns
vif_data["VIF"] = [variance_inflation_factor(x_train.values, i)
                          for i in range(len(x_train.columns))]
print(vif_data)
print('\n')
#VIF values for longitude & latitude exceed 10. Due to this, a new model was 
#examined where the interaction between those two variables were included in the model
print(x_train.columns)
print('\n')

house_regress2 = ols('y_train ~ longitude * latitude + housing_median_age'
                '+ median_income + bedroomhold + roomhold + pophold + ocean_proximity_INLAND +' 
                'ocean_proximity_ISLAND + ocean_proximity_NEARBAY + ocean_proximity_NEAROCEAN',
                  data=cal4).fit()
print('House_Regress2 Summary')
print("\n")
print(house_regress2.summary())
print("\n")
#Adjusted R2 value is higher and the AIC value is lower which suggests that
#house_regress2 is a better model than house_regress1

#Residual plot of the data
pred_val = house_regress2.fittedvalues.copy()
z = cal4['median_house_value']
residual = z - pred_val
# plt.scatter(pred_val, residual)
# plt.title('House_Regress2')
# plt.xlabel('Fitted Values')
# plt.ylabel('Residuals')
#Due to the appearance of heteroscedasticity in the residual plot, the response
#variable was transformed

#Squaring Response Variable
squared = cal4['median_house_value'] **2
house_regress3 = ols('squared ~ longitude * latitude + housing_median_age'
                '+ median_income + bedroomhold + roomhold + pophold + ocean_proximity_INLAND +' 
                'ocean_proximity_ISLAND + ocean_proximity_NEARBAY + ocean_proximity_NEAROCEAN',
                  data=cal4).fit()
print('House_Regress3 Summary')
print("\n")
print(house_regress3.summary())
print("\n")
pred_val1 = house_regress3.fittedvalues.copy()
z1 = cal4['median_house_value'] **2
residual = z1 - pred_val1
# plt.scatter(pred_val1, residual)
# plt.title('House_Regress3')
# plt.xlabel('Fitted Values')
# plt.ylabel('Residuals')

#Square Root of Response Variable
squareroot = np.sqrt(cal4['median_house_value'])
house_regress4 = ols('squareroot ~ longitude * latitude + housing_median_age'
                '+ median_income + bedroomhold + roomhold + pophold + ocean_proximity_INLAND +' 
                'ocean_proximity_ISLAND + ocean_proximity_NEARBAY + ocean_proximity_NEAROCEAN',
                  data=cal4).fit()
print('House_Regress4 Summary')
print("\n")
print(house_regress4.summary())
print("\n")
pred_val2 = house_regress4.fittedvalues.copy()
z2 = np.sqrt(cal4['median_house_value'])
residual = z2 - pred_val2
# plt.scatter(pred_val2, residual)
# plt.title('House_Regress4')
# plt.xlabel('Fitted Values')
# plt.ylabel('Residuals')

#Natural Log of Response Variable
log = np.log(cal4['median_house_value'])
house_regress5 = ols('log ~ longitude * latitude + housing_median_age'
                '+ median_income + bedroomhold + roomhold + pophold + ocean_proximity_INLAND +' 
                'ocean_proximity_ISLAND + ocean_proximity_NEARBAY + ocean_proximity_NEAROCEAN',
                  data=cal4).fit()
print('House_Regress5 Summary')
print("\n")
print(house_regress5.summary())
print("\n")
pred_val3 = house_regress5.fittedvalues.copy()
z3 = np.log(cal4['median_house_value'])
residual = z3 - pred_val3
# plt.scatter(pred_val3, residual)
# plt.title('House_Regress5')
# plt.xlabel('Fitted Values')
# plt.ylabel('Residuals')

#Natural log transformation helps residual plot a little bit but there still seems 
#to be unequal variance. However, this transformation provides the best adjusted
#R2 value and the lowest AIC so this is the model that was selected


#Checking the Normality Assumption
# sns.distplot(residual, bins = 30)
fig, ax = plt.subplots(figsize=(6,2.5))
sp.stats.probplot(residual, plot=ax, fit=True, rvalue = True)


#Using Testing Data to Evaluate Model
predictions = house_regress5.predict(x_test)

# Create a scatterplot of the real test values versus the predicted values. *
# plt.scatter(x = np.log(y_test), y= predictions)
# plt.xlabel('Y_Test')
# plt.ylabel('Predicted Y Values')

from sklearn import metrics
#Mean Absolute Error
print(metrics.mean_absolute_error(np.log(y_test), predictions))
print("\n")
#Mean Squared Error
print(metrics.mean_squared_error(np.log(y_test), predictions))
print("\n")
#Root Mean Squared Error
print(np.sqrt(metrics.mean_squared_error(np.log(y_test), predictions)))


