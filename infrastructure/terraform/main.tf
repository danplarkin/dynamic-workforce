# Main Terraform configuration for Dynamic Workforce Cost Predictor
# Provisions S3, Lambda, SageMaker, API Gateway, and DynamoDB

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for training data and model artifacts
resource "aws_s3_bucket" "model_artifacts" {
  bucket = "${var.project_name}-artifacts-${var.environment}"
  
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# DynamoDB table for prediction results
resource "aws_dynamodb_table" "predictions" {
  name           = "${var.project_name}-predictions-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "prediction_id"
  range_key      = "timestamp"

  attribute {
    name = "prediction_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Lambda function for cost predictions
resource "aws_lambda_function" "cost_predictor" {
  filename         = "../lambda/predictor.zip"
  function_name    = "${var.project_name}-predictor-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "handler.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 512

  environment {
    variables = {
      SAGEMAKER_ENDPOINT = var.sagemaker_endpoint_name
      DYNAMODB_TABLE     = aws_dynamodb_table.predictions.name
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "predictor_api" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "API for workforce cost predictions"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# API Gateway resource
resource "aws_api_gateway_resource" "predict" {
  rest_api_id = aws_api_gateway_rest_api.predictor_api.id
  parent_id   = aws_api_gateway_rest_api.predictor_api.root_resource_id
  path_part   = "predict"
}

# API Gateway method
resource "aws_api_gateway_method" "predict_post" {
  rest_api_id   = aws_api_gateway_rest_api.predictor_api.id
  resource_id   = aws_api_gateway_resource.predict.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway integration with Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.predictor_api.id
  resource_id = aws_api_gateway_resource.predict.id
  http_method = aws_api_gateway_method.predict_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.cost_predictor.invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_predictor.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.predictor_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.predictor_api.id
  stage_name  = var.environment
}
