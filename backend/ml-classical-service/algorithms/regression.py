"""
Regression algorithms for AutoML training.
Provides pre-configured regressors with good default hyperparameters.
"""

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor


def get_random_forest_regressor():
    """
    Random Forest Regressor with balanced hyperparameters.
    Good for most regression tasks, handles non-linear relationships well.
    """
    return RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1  # Use all CPU cores
    )


def get_gradient_boosting_regressor():
    """
    Gradient Boosting Regressor - often achieves high accuracy.
    Slower than Random Forest but can be more accurate.
    """
    return GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )


def get_linear_regression():
    """
    Linear Regression - fast, interpretable baseline model.
    Assumes linear relationship between features and target.
    """
    return LinearRegression(
        n_jobs=-1
    )


def get_ridge_regression():
    """
    Ridge Regression - linear regression with L2 regularization.
    Better than standard linear regression when features are correlated.
    """
    return Ridge(
        alpha=1.0,
        random_state=42,
        solver='auto'
    )


def get_lasso_regression():
    """
    Lasso Regression - linear regression with L1 regularization.
    Performs feature selection by shrinking some coefficients to zero.
    """
    return Lasso(
        alpha=1.0,
        random_state=42,
        max_iter=1000
    )


def get_decision_tree_regressor():
    """
    Decision Tree Regressor - simple, interpretable, fast.
    Good for understanding feature importance.
    """
    return DecisionTreeRegressor(
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
