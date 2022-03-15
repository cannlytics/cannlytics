"""
VAR Functions | Cannlytics
Copyright (c) 2021-2022 Cannlytics
Copyright (c) 2017-2021 Keegan Skeate

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 4/14/2021
Updated: 11/6/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Crude VAR functions.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa import tsatools


def VAR(Vector, lag_order):
    """
    Inputs a Vector of dimension N x I, where N is the number of observations
    and I is the number of variables, as well as the lag order of the model.
    Returns the estimated equations from OLS as a dictionary with names 'Eq#'.
    Args:

    Returns:

    """
    X = np.empty_like(Vector)
    for i in range(1 , 1 + lag_order):
        X = np.column_stack([X, lag(Vector, i)])
    X = np.delete(X, np.s_[0:len(Vector[0])], axis=1)
    X = sm.add_constant(X)   
    VAR_estimates = {}
    for i in range(1,len(Vector[0])+1):
        VAR_estimates["Eq{0}".format(i)] = sm.OLS(Vector[:,[i-1]][lag_order:],
                                                  X[lag_order:]).fit()       
    return VAR_estimates

    
def VAR_forecast(Vector, VAR_estimates, lag_order, horizon,shock=None):
    """
    Inputs the VAR Vector, VAR estimates, the lag order of the model,
    the forecast horizon, and the desired first period shock.
    Args:

    Returns:
    
    """
    # Initial Period shock for IRF.
    if shock is None:
        shock = np.zeros(len(Vector[0]))
    error = np.zeros((len(Vector),len(Vector[0])))
    error[0] = shock
    # Predictions for Forecast Horizon.
    for t in np.arange(0,horizon):     
        X_hat = Vector
        for i in range(1 , lag_order):
            # X_hat = np.column_stack([X_hat, lag(Vector, i)])
            lagged_vector = tsatools.lagmat(Vector, maxlag=1)
            X_hat = np.column_stack([X_hat, lagged_vector])
        X_hat = sm.add_constant(X_hat)     
        Y_hat = []
        for Eq in VAR_estimates:
            Y_hat.append(np.dot(X_hat[-1], VAR_estimates[Eq].params))
        Forecast = Y_hat + error[t]
        Vector = np.vstack((Vector,Forecast))
    return Vector[-horizon:]


def IRF(Vector,VAR_estimates,lag_order,horizon,shock):
    """Impulse response function (IRF).
    Args:

    Returns:
    
    """
    baseline = VAR_forecast(Vector,VAR_estimates,lag_order,horizon,shock=None)
    impact = VAR_forecast(Vector,VAR_estimates,lag_order,horizon,shock=shock.T)
    return (impact-baseline)


def lag_series(series, lag=None):
    """Lag a series.
    Args:

    Returns:
    
    """
    lagged_series = pd.Series(series).shift(1)
    return lagged_series.values


def lag(x, lag=None):
    """Lag a variable.
    Args:

    Returns:
    
    """
    if lag==None: lag=1
    lag_values = np.empty_like(x)
    for i in np.arange(0,len(x)):
        if i>=lag:
            lag_values[i] = x[i-lag]
    return lag_values


def cov_matrix(u):
    """Calculate a covariance matrix.
    Args:
        (u):
    Returns:
        ():
    """
    k = len(u[0])
    matrix = np.ones((k,k))
    for i in np.arange(0,k):
        for j in np.arange(0,k):
            matrix[i][j] = np.cov(u.T[i],u.T[j])[0][1]
    return matrix
