"""Unit tests for predictor Lambda function."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def api_event():
    """Create mock API Gateway event."""
    return {
        "httpMethod": "POST",
        "body": json.dumps({
            "current_employees": 1500,
            "department": "Engineering",
            "average_salary": 85000,
            "turnover_rate": 0.15
        }),
        "headers": {"Content-Type": "application/json"}
    }


def test_lambda_handler_success(api_event):
    """Test successful prediction."""
    with patch('boto3.client') as mock_boto:
        mock_sagemaker = MagicMock()
        mock_sagemaker.invoke_endpoint.return_value = {
            'Body': MagicMock(read=lambda: b'{"predictions": [125000.50]}')
        }
        mock_boto.return_value = mock_sagemaker
        
        from src.lambda_functions.predictor import lambda_handler
        
        response = lambda_handler(api_event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'prediction' in body


def test_lambda_handler_invalid_input():
    """Test with invalid input."""
    invalid_event = {
        "httpMethod": "POST",
        "body": json.dumps({"invalid": "data"}),
        "headers": {"Content-Type": "application/json"}
    }
    
    from src.lambda_functions.predictor import lambda_handler
    
    response = lambda_handler(invalid_event, None)
    assert response['statusCode'] in [400, 500]


def test_lambda_handler_get_method():
    """Test GET method handling."""
    get_event = {
        "httpMethod": "GET",
        "headers": {}
    }
    
    from src.lambda_functions.predictor import lambda_handler
    
    response = lambda_handler(get_event, None)
    assert response['statusCode'] in [200, 405]
