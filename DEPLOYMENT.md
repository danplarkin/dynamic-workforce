# Deployment Guide - Dynamic Workforce Cost Predictor

Complete guide for running this ML prediction API locally and deploying to AWS.

---

## 📋 Prerequisites

### Required Tools
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **AWS CLI** - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Terraform 1.0+** - [Download](https://www.terraform.io/downloads)
- **Git** - Already installed ✓

### AWS Account Setup
1. Create or use existing AWS account
2. Create IAM user with these permissions:
   - S3 (full)
   - Lambda (full)
   - API Gateway (full)
   - SageMaker (full)
   - DynamoDB (full)
   - IAM (create roles)
   - CloudWatch Logs

3. Get Access Keys: IAM Console → Users → Security credentials → Create access key

---

## 🏠 Local Development

### 1. Setup Environment

**PowerShell (Windows):**
```powershell
# Navigate to project
cd C:\Users\danpl\projects\utilities\dynamic-workforce

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Bash (Linux/Mac):**
```bash
# Navigate to project
cd ~/projects/utilities/dynamic-workforce

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Run Tests Locally

**PowerShell (Windows):**
```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_predictor.py -v

# View coverage report
start htmlcov/index.html
```

**Bash (Linux/Mac):**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_predictor.py -v

# View coverage report (Linux)
xdg-open htmlcov/index.html
# Or on Mac
open htmlcov/index.html
```

### 3. Test ML Model Training Locally

**PowerShell & Bash (same commands):**
```bash
# Train model locally (uses training_data.csv)
python src/sagemaker/sagemaker/train_model.py

# This will:
# 1. Load data/training_data.csv
# 2. Train XGBoost model
# 3. Save model locally to models/
# 4. Print evaluation metrics
```

### 4. Test Prediction Lambda Locally

**PowerShell (Windows):**
```powershell
# Create test prediction request
$testRequest = @{
    httpMethod = "POST"
    body = (@{
        current_employees = 1500
        department = "Engineering"
        average_salary = 85000
        turnover_rate = 0.15
        growth_rate = 0.10
    } | ConvertTo-Json)
    headers = @{
        "Content-Type" = "application/json"
    }
} | ConvertTo-Json -Depth 10

# Save to file
$testRequest | Out-File -FilePath test_event.json

# Test Lambda function structure
python -c "
import json
from src.lambda_functions.predictor import lambda_handler

print('Lambda handler is valid and importable')
print('Note: Requires SageMaker endpoint to actually run')
"
```

**Bash (Linux/Mac):**
```bash
# Create test prediction request
cat > test_event.json <<EOF
{
  "httpMethod": "POST",
  "body": "{\"current_employees\": 1500, \"department\": \"Engineering\", \"average_salary\": 85000, \"turnover_rate\": 0.15, \"growth_rate\": 0.10}",
  "headers": {
    "Content-Type": "application/json"
  }
}
EOF

# Test Lambda function structure
python -c "
import json
from src.lambda_functions.predictor import lambda_handler

print('Lambda handler is valid and importable')
print('Note: Requires SageMaker endpoint to actually run')
"
```

### 5. Test API Request Format

**PowerShell & Bash (same commands):**
```bash
# Validate request payload
python -c "
import json

# Example request
request = {
    'current_employees': 1500,
    'department': 'Engineering',
    'average_salary': 85000,
    'turnover_rate': 0.15,
    'growth_rate': 0.10
}

print('Valid prediction request:')
print(json.dumps(request, indent=2))
"
```

---

## ☁️ AWS Deployment

### Step 1: Configure AWS Credentials

```powershell
# Configure AWS CLI (one-time setup)
aws configure

# Enter when prompted:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

### Step 2: Deploy Infrastructure with Terraform

```powershell
# Navigate to Terraform directory
cd infrastructure/terraform

# Initialize Terraform (first time only)
terraform init

# Preview changes
terraform plan

# Review the plan, then deploy
terraform apply

# Type 'yes' when prompted

# Save outputs (API URL, bucket names, etc.)
terraform output
```

**Resources Created:**
- S3 bucket for training data and models
- SageMaker training job and endpoint
- Lambda function for predictions
- API Gateway REST API
- DynamoDB table for prediction logs
- IAM roles and policies
- CloudWatch log groups

### Step 3: Upload Training Data

**PowerShell (Windows):**
```powershell
# Get bucket name from Terraform output
$bucketName = terraform output -raw training_data_bucket

# Upload training data
aws s3 cp ../../data/training_data.csv s3://$bucketName/data/training_data.csv

# Verify upload
aws s3 ls s3://$bucketName/data/
```

**Bash (Linux/Mac):**
```bash
# Get bucket name from Terraform output
BUCKET_NAME=$(terraform output -raw training_data_bucket)

# Upload training data
aws s3 cp ../../data/training_data.csv s3://$BUCKET_NAME/data/training_data.csv

# Verify upload
aws s3 ls s3://$BUCKET_NAME/data/
```

### Step 4: Train SageMaker Model

**Option A: Using Python Script**

PowerShell (Windows):
```powershell
# Set environment variables
$env:AWS_REGION = "us-east-1"
$env:TRAINING_DATA_BUCKET = $bucketName

# Run training script
cd ../../src/sagemaker/sagemaker
python train_model.py
```

Bash (Linux/Mac):
```bash
# Set environment variables
export AWS_REGION="us-east-1"
export TRAINING_DATA_BUCKET=$BUCKET_NAME

# Run training script
cd ../../src/sagemaker/sagemaker
python train_model.py
```

**Option B: Using AWS Console**
1. Go to SageMaker Console → Training Jobs
2. Create training job
3. Use training data from S3
4. Select ml.m5.xlarge instance
5. Wait ~10-15 minutes for training

**Option C: Using AWS CLI**

PowerShell (Windows):
```powershell
# Create training job
aws sagemaker create-training-job `
    --training-job-name "workforce-predictor-$(Get-Date -Format 'yyyyMMdd-HHmmss')" `
    --algorithm-specification TrainingImage=<ecr-image>,TrainingInputMode=File `
    --role-arn $(terraform output -raw sagemaker_role_arn) `
    --input-data-config '[{"ChannelName":"training","DataSource":{"S3DataSource":{"S3DataType":"S3Prefix","S3Uri":"s3://'$bucketName'/data/"}}}]' `
    --output-data-config S3OutputPath=s3://$bucketName/models/ `
    --resource-config InstanceType=ml.m5.xlarge,InstanceCount=1,VolumeSizeInGB=10 `
    --stopping-condition MaxRuntimeInSeconds=3600
```

Bash (Linux/Mac):
```bash
# Create training job
aws sagemaker create-training-job \
    --training-job-name "workforce-predictor-$(date +%Y%m%d-%H%M%S)" \
    --algorithm-specification TrainingImage=<ecr-image>,TrainingInputMode=File \
    --role-arn $(terraform output -raw sagemaker_role_arn) \
    --input-data-config "[{\"ChannelName\":\"training\",\"DataSource\":{\"S3DataSource\":{\"S3DataType\":\"S3Prefix\",\"S3Uri\":\"s3://$BUCKET_NAME/data/\"}}}]" \
    --output-data-config S3OutputPath=s3://$BUCKET_NAME/models/ \
    --resource-config InstanceType=ml.m5.xlarge,InstanceCount=1,VolumeSizeInGB=10 \
    --stopping-condition MaxRuntimeInSeconds=3600
```

### Step 5: Deploy SageMaker Endpoint

**PowerShell & Bash (same commands):**
```bash
# After training completes, deploy endpoint
cd src/sagemaker/sagemaker
python deploy_endpoint.py

# This will:
# 1. Create SageMaker model from training job
# 2. Create endpoint configuration
# 3. Deploy endpoint (takes ~5-10 minutes)
# 4. Print endpoint name
```

### Step 6: Test the API

**PowerShell (Windows):**
```powershell
# Get API URL from Terraform
$apiUrl = terraform output -raw api_gateway_url

# Test prediction endpoint
$body = @{
    current_employees = 1500
    department = "Engineering"
    average_salary = 85000
    turnover_rate = 0.15
    growth_rate = 0.10
} | ConvertTo-Json

# Make prediction request
$response = Invoke-RestMethod -Uri "$apiUrl/predict" -Method POST -Body $body -ContentType "application/json"

# View prediction
$response | ConvertTo-Json -Depth 10
```

**Bash (Linux/Mac):**
```bash
# Get API URL from Terraform
API_URL=$(terraform output -raw api_gateway_url)

# Test prediction endpoint with curl
curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "current_employees": 1500,
    "department": "Engineering",
    "average_salary": 85000,
    "turnover_rate": 0.15,
    "growth_rate": 0.10
  }'
```

### Step 7: Monitor Execution

**PowerShell (Windows):**
```powershell
# View Lambda logs
aws logs tail /aws/lambda/workforce-predictor --follow

# Check DynamoDB predictions table
$tableName = terraform output -raw predictions_table_name
aws dynamodb scan --table-name $tableName --max-items 5

# Monitor SageMaker endpoint
$endpointName = terraform output -raw sagemaker_endpoint_name
aws sagemaker describe-endpoint --endpoint-name $endpointName
```

**Bash (Linux/Mac):**
```bash
# View Lambda logs
aws logs tail /aws/lambda/workforce-predictor --follow

# Check DynamoDB predictions table
TABLE_NAME=$(terraform output -raw predictions_table_name)
aws dynamodb scan --table-name $TABLE_NAME --max-items 5

# Monitor SageMaker endpoint
ENDPOINT_NAME=$(terraform output -raw sagemaker_endpoint_name)
aws sagemaker describe-endpoint --endpoint-name $ENDPOINT_NAME
```

---

## 🧪 Testing in AWS

### Test API with curl (if installed)

```bash
# Using curl
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{
    "current_employees": 2000,
    "department": "Sales",
    "average_salary": 75000,
    "turnover_rate": 0.20,
    "growth_rate": 0.15
  }'
```

### Test API with PowerShell

```powershell
# Multiple test scenarios
$scenarios = @(
    @{ name = "Small Dept"; current_employees = 500; department = "HR"; average_salary = 65000; turnover_rate = 0.10; growth_rate = 0.05 },
    @{ name = "Large Dept"; current_employees = 3000; department = "Engineering"; average_salary = 95000; turnover_rate = 0.18; growth_rate = 0.20 },
    @{ name = "High Turnover"; current_employees = 1000; department = "Sales"; average_salary = 70000; turnover_rate = 0.35; growth_rate = 0.10 }
)

$apiUrl = terraform output -raw api_gateway_url

foreach ($scenario in $scenarios) {
    Write-Host "`n=== Testing: $($scenario.name) ===" -ForegroundColor Cyan
    $body = $scenario | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$apiUrl/predict" -Method POST -Body $body -ContentType "application/json"
    Write-Host "Predicted Cost: $($response.predicted_cost)" -ForegroundColor Green
}
```

### Batch Predictions

```powershell
# Process multiple predictions
$predictions = Import-Csv test_scenarios.csv | ForEach-Object {
    $body = @{
        current_employees = [int]$_.current_employees
        department = $_.department
        average_salary = [int]$_.average_salary
        turnover_rate = [double]$_.turnover_rate
        growth_rate = [double]$_.growth_rate
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$apiUrl/predict" -Method POST -Body $body -ContentType "application/json"
    
    [PSCustomObject]@{
        Department = $_.department
        Employees = $_.current_employees
        PredictedCost = $response.predicted_cost
    }
}

$predictions | Format-Table -AutoSize
```

---

## 📊 Monitoring & Troubleshooting

### Check SageMaker Endpoint Status

```powershell
# Get endpoint status
aws sagemaker describe-endpoint --endpoint-name workforce-predictor-endpoint

# View endpoint metrics
aws cloudwatch get-metric-statistics `
    --namespace AWS/SageMaker `
    --metric-name ModelLatency `
    --dimensions Name=EndpointName,Value=workforce-predictor-endpoint Name=VariantName,Value=AllTraffic `
    --start-time (Get-Date).AddHours(-1) `
    --end-time (Get-Date) `
    --period 3600 `
    --statistics Average,Maximum
```

### Check Lambda Performance

```powershell
# Lambda invocation metrics
aws cloudwatch get-metric-statistics `
    --namespace AWS/Lambda `
    --metric-name Duration `
    --dimensions Name=FunctionName,Value=workforce-predictor `
    --start-time (Get-Date).AddHours(-1) `
    --end-time (Get-Date) `
    --period 300 `
    --statistics Average,Maximum

# View recent errors
aws logs filter-log-events `
    --log-group-name /aws/lambda/workforce-predictor `
    --filter-pattern "ERROR" `
    --start-time ((Get-Date).AddHours(-1).ToUniversalTime() | Get-Date -UFormat %s) `
    --max-items 10
```

### Common Issues

**Issue: SageMaker endpoint not found**
```powershell
# Verify endpoint exists
aws sagemaker list-endpoints

# If missing, redeploy
cd src/sagemaker/sagemaker
python deploy_endpoint.py
```

**Issue: Lambda timeout**
- SageMaker inference can take 2-5 seconds
- Increase Lambda timeout in [infrastructure/terraform/main.tf](infrastructure/terraform/main.tf) to 30 seconds

**Issue: Prediction accuracy issues**
- Retrain model with more data
- Check training metrics in CloudWatch
- Validate training data quality in [data/training_data.csv](data/training_data.csv)

**Issue: API Gateway 502 errors**
- Check Lambda execution role permissions
- Verify Lambda can invoke SageMaker endpoint
- Review CloudWatch logs

---

## 💰 Cost Management

### Estimate Monthly Costs

```powershell
# View cost breakdown
aws ce get-cost-and-usage `
    --time-period Start=2025-12-01,End=2025-12-28 `
    --granularity MONTHLY `
    --metrics UnblendedCost `
    --group-by Type=SERVICE `
    --filter file://cost-filter.json
```

**Typical Monthly Costs:**
- **SageMaker Endpoint** (ml.t2.medium 24/7): ~$35/month
- **Lambda** (1000 invocations/month): ~$0.20/month
- **API Gateway** (1000 requests/month): ~$0.04/month
- **S3 Storage** (<1GB): ~$0.02/month
- **DynamoDB** (on-demand): ~$1/month
- **CloudWatch Logs**: ~$0.50/month

**Total: ~$37/month**

### Cost Optimization

**Option 1: Use Serverless Inference (lower cost)**
```powershell
# Modify deploy_endpoint.py to use serverless
# Change instance type to 'serverless'
# Costs only when invoked (~$0.20 per 1000 invocations)
```

**Option 2: Stop endpoint when not in use**
```powershell
# Delete endpoint (keeps model)
aws sagemaker delete-endpoint --endpoint-name workforce-predictor-endpoint

# Recreate when needed
python src/sagemaker/sagemaker/deploy_endpoint.py
```

**Option 3: Use smaller instance**
```powershell
# Change to ml.t2.medium instead of ml.m5.xlarge
# Update in infrastructure/terraform/variables.tf
```

---

## 🔄 Development Workflow

### Update Model

```powershell
# 1. Update training data
# Edit data/training_data.csv with new data

# 2. Upload to S3
$bucketName = terraform output -raw training_data_bucket
aws s3 cp data/training_data.csv s3://$bucketName/data/training_data.csv

# 3. Retrain model
cd src/sagemaker/sagemaker
python train_model.py

# 4. Deploy new endpoint
python deploy_endpoint.py

# 5. Test predictions
cd ../../../infrastructure/terraform
$apiUrl = terraform output -raw api_gateway_url
# Run test predictions...
```

### Update Lambda Function

```powershell
# 1. Make code changes in src/lambda_functions/predictor.py

# 2. Run tests
pytest tests/unit/test_predictor.py

# 3. Deploy changes
cd infrastructure/terraform
terraform apply -auto-approve

# 4. Test API
$apiUrl = terraform output -raw api_gateway_url
# Run test predictions...
```

---

## 🗑️ Cleanup / Destroy Resources

### Important: Delete Endpoint First (saves money)

```powershell
# Delete SageMaker endpoint (most expensive resource)
$endpointName = terraform output -raw sagemaker_endpoint_name
aws sagemaker delete-endpoint --endpoint-name $endpointName

# Wait for deletion
aws sagemaker wait endpoint-deleted --endpoint-name $endpointName
```

### Destroy All Resources

```powershell
cd infrastructure/terraform

# Preview what will be destroyed
terraform plan -destroy

# Empty S3 buckets first
$bucketName = terraform output -raw training_data_bucket
aws s3 rm s3://$bucketName --recursive

# Destroy all resources
terraform destroy

# Type 'yes' when prompted
```

---

## 🚀 Quick Start Commands

**PowerShell (Windows):**
```powershell
# Complete local setup
cd C:\Users\danpl\projects\utilities\dynamic-workforce
pip install -r requirements.txt -r requirements-dev.txt
pytest

# Complete AWS deployment
aws configure
cd infrastructure/terraform
terraform init
terraform apply
$bucketName = terraform output -raw training_data_bucket
aws s3 cp ../../data/training_data.csv s3://$bucketName/data/training_data.csv
cd ../../src/sagemaker/sagemaker
python train_model.py
python deploy_endpoint.py

# Test API
cd ../../../infrastructure/terraform
$apiUrl = terraform output -raw api_gateway_url
Invoke-RestMethod -Uri "$apiUrl/predict" -Method POST -Body '{"current_employees":1500,"department":"Engineering","average_salary":85000,"turnover_rate":0.15,"growth_rate":0.10}' -ContentType "application/json"
```

**Bash (Linux/Mac):**
```bash
# Complete local setup
cd ~/projects/utilities/dynamic-workforce
pip install -r requirements.txt -r requirements-dev.txt
pytest

# Complete AWS deployment
aws configure
cd infrastructure/terraform
terraform init
terraform apply
BUCKET_NAME=$(terraform output -raw training_data_bucket)
aws s3 cp ../../data/training_data.csv s3://$BUCKET_NAME/data/training_data.csv
cd ../../src/sagemaker/sagemaker
python train_model.py
python deploy_endpoint.py

# Test API
cd ../../../infrastructure/terraform
API_URL=$(terraform output -raw api_gateway_url)
curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"current_employees":1500,"department":"Engineering","average_salary":85000,"turnover_rate":0.15,"growth_rate":0.10}'
```

---

## 📚 Additional Resources

- [Amazon SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Project README](README.md)

---

## 🆘 Getting Help

**Local Development Issues**: Check [tests/unit/test_predictor.py](tests/unit/test_predictor.py)

**Model Training Issues**: Review [src/sagemaker/sagemaker/train_model.py](src/sagemaker/sagemaker/train_model.py)

**API Issues**: Check [infrastructure/terraform/main.tf](infrastructure/terraform/main.tf) API Gateway config

**CI/CD Issues**: Check [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
