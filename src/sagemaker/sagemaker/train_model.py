"""
SageMaker training script for workforce cost prediction model.
Uses XGBoost for regression.
"""

import pandas as pd
import numpy as np
import boto3
import argparse
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score


def load_data(data_path):
    """Load training data from CSV."""
    df = pd.read_csv(data_path)
    return df


def preprocess_data(df):
    """Preprocess data for training."""
    # Encode categorical variables
    le = LabelEncoder()
    if 'department' in df.columns:
        df['department_encoded'] = le.fit_transform(df['department'])
    
    # Define features and target
    feature_columns = ['headcount', 'avg_salary', 'turnover_rate', 'benefits_multiplier']
    if 'department_encoded' in df.columns:
        feature_columns.append('department_encoded')
    
    X = df[feature_columns]
    y = df['annual_cost']
    
    return X, y, le


def train_model(X_train, y_train, X_test, y_test):
    """Train XGBoost model."""
    # Define model
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    
    # Train model
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    
    print(f"Training RMSE: {train_rmse:.2f}")
    print(f"Test RMSE: {test_rmse:.2f}")
    print(f"Training R²: {train_r2:.4f}")
    print(f"Test R²: {test_r2:.4f}")
    
    return model


def save_model(model, label_encoder, output_path):
    """Save trained model and preprocessor."""
    os.makedirs(output_path, exist_ok=True)
    
    # Save model
    model_file = os.path.join(output_path, 'model.pkl')
    joblib.dump(model, model_file)
    
    # Save label encoder
    encoder_file = os.path.join(output_path, 'label_encoder.pkl')
    joblib.dump(label_encoder, encoder_file)
    
    print(f"Model saved to {model_file}")
    print(f"Label encoder saved to {encoder_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', type=str, default='../data/training_data.csv')
    parser.add_argument('--output-path', type=str, default='./model_artifacts')
    args = parser.parse_args()
    
    print("Loading data...")
    df = load_data(args.data_path)
    
    print("Preprocessing data...")
    X, y, label_encoder = preprocess_data(df)
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("Training model...")
    model = train_model(X_train, y_train, X_test, y_test)
    
    print("Saving model...")
    save_model(model, label_encoder, args.output_path)
    
    print("Training complete!")
