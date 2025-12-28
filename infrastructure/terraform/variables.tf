# Terraform variables for Dynamic Workforce Cost Predictor

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "dynamic-workforce"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "sagemaker_endpoint_name" {
  description = "Name of the SageMaker endpoint"
  type        = string
  default     = "workforce-cost-predictor-endpoint"
}
