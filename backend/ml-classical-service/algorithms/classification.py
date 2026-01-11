"""
Classification algorithms for AutoML training.
Provides pre-configured classifiers with good default hyperparameters.
"""

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier


def get_random_forest_classifier():
    """
    Random Forest Classifier with balanced hyperparameters.
    Good for most classification tasks, handles non-linear relationships well.
    """
    return RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1  # Use all CPU cores
    )


def get_gradient_boosting_classifier():
    """
    Gradient Boosting Classifier - often achieves high accuracy.
    Slower than Random Forest but can be more accurate.
    """
    return GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )


def get_logistic_regression():
    """
    Logistic Regression - fast, interpretable linear model.
    Good baseline for binary and multi-class classification.
    """
    return LogisticRegression(
        max_iter=1000,
        random_state=42,
        solver='lbfgs',
        multi_class='auto'
    )


def get_svm_classifier():
    """
    Support Vector Machine - effective in high-dimensional spaces.
    Works well with clear margin of separation.
    """
    return SVC(
        kernel='rbf',
        C=1.0,
        gamma='scale',
        random_state=42,
        probability=True  # Enable probability estimates
    )


def get_decision_tree_classifier():
    """
    Decision Tree Classifier - simple, interpretable, fast.
    Good for understanding feature importance.
    """
    return DecisionTreeClassifier(
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )


def get_knn_classifier():
    """
    K-Nearest Neighbors Classifier - instance-based learning.
    Simple and effective for smaller datasets.
    """
    return KNeighborsClassifier(
        n_neighbors=5,
        weights='distance',  # Weight by inverse distance
        algorithm='auto',
        n_jobs=-1  # Use all CPU cores
    )


def get_naive_bayes_classifier():
    """
    Gaussian Naive Bayes - fast probabilistic classifier.
    Assumes features are independent. Good for text and simple classification.
    """
    return GaussianNB()


def get_neural_network_classifier():
    """
    Multi-Layer Perceptron (Neural Network) - powerful deep learning.
    Can learn complex non-linear patterns.
    """
    return MLPClassifier(
        hidden_layer_sizes=(100, 50),  # Two hidden layers
        activation='relu',
        solver='adam',
        alpha=0.0001,  # L2 regularization
        batch_size='auto',
        learning_rate='adaptive',
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1
    )
