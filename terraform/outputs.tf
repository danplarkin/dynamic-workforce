# Terraform outputs

output "api_gateway_url" {
  description = "URL of the API Gateway endpoint"
  value       = "${aws_api_gateway_deployment.api_deployment.invoke_url}/predict"
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for model artifacts"
  value       = aws_s3_bucket.model_artifacts.id
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for predictions"
  value       = aws_dynamodb_table.predictions.name
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.cost_predictor.function_name
}
