import pandas as pd         # for creating data frame
import numpy as np          # used to support large, multi-dimensional arrays

from datetime import date   # for todays date
from datetime import datetime # for runtime of program

import statsmodels.api as sm
import statsmodels.formula.api as smf

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.linear_model import GammaRegressor
from sklearn.ensemble import GradientBoostingRegressor

from sklearn.model_selection import train_test_split

merged = pd.read_csv('/home/charlie/Documents/myProjects/Gumtree-bargains/completeTV.csv')


#### REGRESSION ####

predictors = list(merged)[1:len(merged)]
predictors.remove('Price')
predictors.remove('Suburb')
predictors.remove('Date Listed')
predictors.remove('Last Edited')
predictors.remove('size_inch')
predictors.remove('yhat') # this column will already exist if this script has been run before

merged_dummies = pd.get_dummies(merged, dummy_na = True, drop_first = True, columns=predictors)

X = merged_dummies.drop(columns=['Url', 'Price', 'Suburb', 'Date Listed', 'Last Edited', 'yhat']) # skips url column
X['size_inch'] = merged['size_inch']
X['size_na'] = np.isnan(X['size_inch']) # this currently doesnt work
X['size_inch'] = np.nan_to_num(X['size_inch'])
# do a tv age * brand here

y = merged['Price']
y = np.nan_to_num(y)
print(y)

# Data splitting
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0, train_size = 0.7)


### Linear Regression
linReg = LinearRegression().fit(X_train, y_train)

linRegR_sq = linReg.score(X_test, y_test)
print('linReg: coefficient of determination:', linRegR_sq)

merged['yhat'] = linReg.predict(X)

### GLM with Gamma (doesnt work since some y values are either zero or missing, not sure which)


# gamReg = GammaRegressor().fit(X,y)
# gamRegR_sq = gamReg.score(X,y)
# print('gamReg: coefficient of determination:', gamRegR_sq)

# merged['gamReg'] = gamReg.predict(X)


## RANDOM FOREST
rf = RandomForestRegressor(max_depth=2, random_state=0)
rf.fit(X_train, y_train)

rfR_sq = rf.score(X_test,y_test)
print('rf: coefficient of determination:', rfR_sq)

merged['rf'] = rf.predict(X)

## GRADIENT BOOSTING
gbm = GradientBoostingRegressor(random_state=0)
gbm.fit(X_train, y_train)
print('gbm: coefficient of determination:', gbm.score(X_test, y_test))

merged['gbm'] = gbm.predict(X)



# write finished file
merged.to_csv('/home/charlie/Documents/myProjects/Gumtree-bargains/completeTVTEST.csv', header=True, index = False)