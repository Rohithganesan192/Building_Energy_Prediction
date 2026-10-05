"""
preprocessing.py
================
Model-specific preprocessing pipelines.
Fitted on TRAIN only. Applied to Validation/Test.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class LinearPreprocessor:
    """
    Preprocessing for Linear Regression.
    - Numerical: Median imputation + StandardScaler
    - Categorical: OneHotEncoder
    """
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        
        num_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        cat_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', num_transformer, self.num_cols),
                ('cat', cat_transformer, self.cat_cols)
            ]
        )
        self.feature_names_out_ = None

    def fit(self, X: pd.DataFrame, y=None):
        self.preprocessor.fit(X)
        
        # Get feature names if possible
        try:
            cat_features = self.preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(self.cat_cols)
            self.feature_names_out_ = list(self.num_cols) + list(cat_features)
        except Exception:
            pass
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_trans = self.preprocessor.transform(X)
        if self.feature_names_out_ is not None and X_trans.shape[1] == len(self.feature_names_out_):
            return pd.DataFrame(X_trans, columns=self.feature_names_out_, index=X.index)
        return pd.DataFrame(X_trans, index=X.index)


class SklearnTreePreprocessor:
    """
    Preprocessing for standard scikit-learn trees (DecisionTree, RandomForest).
    - Numerical: Median imputation (sklearn trees do not natively support NaN)
    - Categorical: OrdinalEncoder (sklearn trees need numeric input)
    - No scaling needed.
    """
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        
        num_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median'))
        ])
        
        cat_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
        ])
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', num_transformer, self.num_cols),
                ('cat', cat_transformer, self.cat_cols)
            ]
        )
        self.feature_names_out_ = list(self.num_cols) + list(self.cat_cols)

    def fit(self, X: pd.DataFrame, y=None):
        self.preprocessor.fit(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_trans = self.preprocessor.transform(X)
        return pd.DataFrame(X_trans, columns=self.feature_names_out_, index=X.index)


class XGBoostPreprocessor:
    """
    Preprocessing for XGBoost.
    - Numerical: Left as is (NaNs natively handled by XGBoost).
    - Categorical: OrdinalEncoder (safest version-agnostic representation).
    """
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        
        cat_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
        ])
        
        # remainder='passthrough' keeps the numerical columns untouched
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('cat', cat_transformer, self.cat_cols)
            ],
            remainder='passthrough'
        )
        # Order after ColumnTransformer: first cat_cols, then num_cols (remainder)
        self.feature_names_out_ = list(self.cat_cols) + list(self.num_cols)

    def fit(self, X: pd.DataFrame, y=None):
        self.preprocessor.fit(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_trans = self.preprocessor.transform(X)
        return pd.DataFrame(X_trans, columns=self.feature_names_out_, index=X.index)


class LightGBMPreprocessor:
    """
    Preprocessing for LightGBM.
    - Numerical: Left as is (NaNs natively handled).
    - Categorical: Cast to pandas 'category' dtype (natively handled).
    """
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_out = X[self.num_cols + self.cat_cols].copy()
        for col in self.cat_cols:
            X_out[col] = X_out[col].astype('category')
        return X_out


class CatBoostPreprocessor:
    """
    Preprocessing for CatBoost.
    - Numerical: Left as is.
    - Categorical: Filled with "Missing" string so CatBoost's native 
      cat_features engine can parse them without NaN errors.
    """
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_out = X[self.num_cols + self.cat_cols].copy()
        for col in self.cat_cols:
            # CatBoost expects strings or ints, and doesn't like float NaNs in categorical
            X_out[col] = X_out[col].fillna("Missing").astype(str)
        return X_out


def get_preprocessor(model_name: str, num_cols: list, cat_cols: list):
    """
    Returns the appropriate fitted preprocessor based on model type.
    """
    if model_name in ["LinearRegression"]:
        return LinearPreprocessor(num_cols, cat_cols)
    elif model_name in ["DecisionTree", "RandomForest"]:
        return SklearnTreePreprocessor(num_cols, cat_cols)
    elif model_name == "XGBoost":
        return XGBoostPreprocessor(num_cols, cat_cols)
    elif model_name == "LightGBM":
        return LightGBMPreprocessor(num_cols, cat_cols)
    elif model_name == "CatBoost":
        return CatBoostPreprocessor(num_cols, cat_cols)
    else:
        raise ValueError(f"Unknown model_name: {model_name}")
