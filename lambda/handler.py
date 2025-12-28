"""
Lambda function for workforce cost prediction.
Invokes SageMaker endpoint and stores results in DynamoDB.
"""

import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict

# Initialize AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
SAGEMAKER_ENDPOINT = os.environ['SAGEMAKER_ENDPOINT']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
table = dynamodb.Table(DYNAMODB_TABLE)


def lambda_handler(event, context):
    """
    Main Lambda handler for cost predictions.
    
    Args:
        event: API Gateway event with prediction request
        context: Lambda context
    
    Returns:
        dict: API Gateway response with prediction
    """
    try:
        # Parse request body
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        # Validate required fields
        required_fields = ['headcount', 'avg_salary', 'turnover_rate']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Get prediction from SageMaker
        prediction_result = get_prediction_from_sagemaker(body)
        
        # Generate prediction ID and timestamp
        prediction_id = f"pred_{uuid.uuid4().hex[:8]}"
        timestamp = int(datetime.now().timestamp())
        
        # Store prediction in DynamoDB
        store_prediction(prediction_id, timestamp, body, prediction_result)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'prediction_id': prediction_id,
                'predicted_annual_cost': prediction_result['predicted_cost'],
                'confidence_interval': prediction_result.get('confidence_interval', []),
                'timestamp': timestamp,
                'input_parameters': body
            })
        }
        
    except Exception as e:
        print(f"Error processing prediction: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def get_prediction_from_sagemaker(input_data: Dict) -> Dict:
    """
    Call SageMaker endpoint for prediction.
    
    Args:
        input_data: Input features for prediction
    
    Returns:
        dict: Prediction results
    """
    # Prepare input for SageMaker
    features = {
        'headcount': input_data['headcount'],
        'avg_salary': input_data['avg_salary'],
        'turnover_rate': input_data['turnover_rate'],
        'benefits_multiplier': input_data.get('benefits_multiplier', 1.35),
        'department': input_data.get('department', 'General')
    }
    
    # Invoke SageMaker endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType='application/json',
        Body=json.dumps(features)
    )
    
    # Parse response
    result = json.loads(response['Body'].read().decode())
    
    # Calculate predicted annual cost
    # Formula: headcount * avg_salary * benefits_multiplier * (1 + turnover_rate * turnover_cost_multiplier)
    predicted_cost = result.get('prediction', 0)
    
    # Calculate confidence interval (simplified - in real scenario, this comes from model)
    confidence_interval = [
        predicted_cost * 0.95,
        predicted_cost * 1.05
    ]
    
    return {
        'predicted_cost': round(predicted_cost, 2),
        'confidence_interval': [round(x, 2) for x in confidence_interval]
    }


def store_prediction(prediction_id: str, timestamp: int, input_data: Dict, prediction_result: Dict):
    """
    Store prediction results in DynamoDB.
    
    Args:
        prediction_id: Unique prediction identifier
        timestamp: Unix timestamp
        input_data: Input parameters
        prediction_result: Prediction output
    """
    item = {
        'prediction_id': prediction_id,
        'timestamp': timestamp,
        'headcount': input_data['headcount'],
        'avg_salary': input_data['avg_salary'],
        'turnover_rate': input_data['turnover_rate'],
        'department': input_data.get('department', 'General'),
        'benefits_multiplier': input_data.get('benefits_multiplier', 1.35),
        'predicted_cost': prediction_result['predicted_cost'],
        'confidence_interval_low': prediction_result['confidence_interval'][0],
        'confidence_interval_high': prediction_result['confidence_interval'][1]
    }
    
    table.put_item(Item=item)
    print(f"Stored prediction: {prediction_id}")
