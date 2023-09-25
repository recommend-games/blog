import numpy as np
from scipy.optimize import fmin_slsqp
from sklearn.linear_model import LinearRegression, Ridge


def train_weights_lr(X_train, y_train, model=None):
    if model is None:
        model = LinearRegression(fit_intercept=False)

    return model.fit(X_train, y_train).coef_


def train_weights_slsqp(X_train, y_train):
    def loss(weights):
        return np.sqrt(np.mean((y_train - X_train.dot(weights)) ** 2))

    weights_init = np.ones(X_train.shape[1]) / X_train.shape[1]

    return fmin_slsqp(
        func=loss,
        x0=weights_init,
        f_eqcons=lambda weights: np.sum(weights) - 1,
        bounds=[(0.0, 1.0)] * len(weights_init),
        disp=False,
    )


def weights_and_predictions(model, X_train, y_train, X_test):
    if model == "linear":
        weights = train_weights_lr(
            X_train,
            y_train,
            model=LinearRegression(fit_intercept=False),
        )
    elif model == "ridge":
        weights = train_weights_lr(
            X_train,
            y_train,
            model=Ridge(fit_intercept=False, alpha=100.0),
        )
    elif model == "slsqp":
        weights = train_weights_slsqp(X_train, y_train)
    else:
        raise ValueError(f"Unknown model: {model}")

    pred = np.concatenate((X_train.dot(weights), X_test.dot(weights)))

    return weights, pred
