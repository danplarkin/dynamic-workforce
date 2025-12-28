"""
SageMaker inference script for real-time predictions.
"""

import joblib
import json
import numpy as np
import os


def model_fn(model_dir):
    """Load model and preprocessor."""
    model = joblib.load(os.path.join(model_dir, 'model.pkl'))
    label_encoder = joblib.load(os.path.join(model_dir, 'label_encoder.pkl'))
    return {'model': model, 'label_encoder': label_encoder}


def input_fn(request_body, content_type='application/json'):
    """Parse input data."""
    if content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def predict_fn(input_data, model_dict):
    """Make prediction."""
    model = model_dict['model']
    label_encoder = model_dict['label_encoder']
    
    # Prepare features
    features = [
        input_data['headcount'],
        input_data['avg_salary'],
        input_data['turnover_rate'],
        input_data.get('benefits_multiplier', 1.35)
    ]
    
    # Encode department if provided
    if 'department' in input_data:
        try:
            dept_encoded = label_encoder.transform([input_data['department']])[0]
            features.append(dept_encoded)
        except:
            features.append(0)  # Default encoding
    
    # Make prediction
    features_array = np.array([features])
    prediction = model.predict(features_array)[0]
    
    return {'prediction': float(prediction)}


def output_fn(prediction, accept='application/json'):
    """Format output."""
    if accept == 'application/json':
        return json.dumps(prediction), accept
    else:
        raise ValueError(f"Unsupported accept type: {accept}")
