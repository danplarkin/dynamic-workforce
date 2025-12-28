"""
Script to deploy trained model to SageMaker endpoint.
"""

import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel
from datetime import datetime
import argparse


def deploy_model(model_artifacts_s3_path, endpoint_name, role_arn):
    """
    Deploy model to SageMaker endpoint.
    
    Args:
        model_artifacts_s3_path: S3 path to model artifacts
        endpoint_name: Name for the endpoint
        role_arn: IAM role ARN for SageMaker
    """
    # Create SageMaker session
    sagemaker_session = sagemaker.Session()
    
    # Define model
    sklearn_model = SKLearnModel(
        model_data=model_artifacts_s3_path,
        role=role_arn,
        entry_point='inference.py',
        framework_version='1.2-1',
        py_version='py3',
        sagemaker_session=sagemaker_session
    )
    
    # Deploy model
    print(f"Deploying model to endpoint: {endpoint_name}")
    predictor = sklearn_model.deploy(
        initial_instance_count=1,
        instance_type='ml.t2.medium',
        endpoint_name=endpoint_name
    )
    
    print(f"Model deployed successfully to endpoint: {endpoint_name}")
    return predictor


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-s3-path', type=str, required=True,
                        help='S3 path to model artifacts (s3://bucket/path/model.tar.gz)')
    parser.add_argument('--endpoint-name', type=str, default='workforce-cost-predictor-endpoint')
    parser.add_argument('--role-arn', type=str, required=True,
                        help='SageMaker execution role ARN')
    args = parser.parse_args()
    
    deploy_model(args.model_s3_path, args.endpoint_name, args.role_arn)
