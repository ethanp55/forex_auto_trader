from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler as SklearnMinMaxScaler
from sklearn.utils.validation import check_array


class MinMaxScaler(BaseEstimator, TransformerMixin):
    def __init__(self, sample_range=(0, 1)):
        self.sample_range = sample_range

    def fit(self, X=None, y=None):
        """Pass.
        Parameters
        ----------
        X
            Ignored
        y
            Ignored
        Returns
        -------
        self : object
        """
        return self

    def transform(self, X):
        """Scale samples of X according to sample_range.
        Parameters
        ----------
        X : array-like, shape = (n_samples, n_timestamps)
            Data to scale.
        Returns
        -------
        X_new : array-like, shape = (n_samples, n_timestamps)
            Scaled data.
        """
        X = check_array(X, dtype='float64')
        scaler = SklearnMinMaxScaler(feature_range=self.sample_range)
        X_new = scaler.fit_transform(X.T).T
        return X_new
