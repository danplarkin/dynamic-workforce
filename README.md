# Dynamic Workforce Cost Predictor

A machine learning-powered application that predicts workforce costs using AWS SageMaker and provides real-time predictions via API Gateway.

## Architecture Diagram

```
HR Data → S3 → Lambda → SageMaker Endpoint → DynamoDB → QuickSight Dashboard
```

## Tech Stack

- **AWS Services:** S3, Lambda, SageMaker, DynamoDB, QuickSight, API Gateway
- **IaC:** Terraform or AWS CDK
- **Language:** Python for Lambda & ML model
- **Visualization:** QuickSight dashboard

## Project Overview

This project demonstrates expertise in:
- Machine Learning model training and deployment
- SageMaker endpoint management
- API Gateway integration
- Real-time prediction pipelines
- Cost optimization strategies
- HR Tech analytics

## Step-by-Step Implementation

1. **Deploy infrastructure** with Terraform/CDK (S3, Lambda, SageMaker endpoint, DynamoDB, QuickSight via IaC)
2. **Train regression model** in SageMaker using sample HR cost data
3. **Create Lambda + API Gateway** for cost prediction requests
4. **Store predictions** in DynamoDB
5. **Visualize predictions** in QuickSight dashboard
6. **Automate deployment** with IaC

## Repository Structure

```
/workforce-cost-predictor
├── terraform/       # IaC scripts
├── lambda/          # API Gateway + Lambda code
├── sagemaker/       # Model training scripts
├── data/            # Sample HR cost data
└── README.md        # Setup guide
```

## Getting Started

### Prerequisites

- AWS Account with SageMaker permissions
- Terraform or AWS CDK installed
- Python 3.9+
- AWS CLI configured
- Basic ML knowledge (scikit-learn, pandas)

### Installation

```bash
# Clone the repository
git clone https://github.com/danplarkin/dynamic-workforce.git
cd dynamic-workforce

# Train and deploy SageMaker model
cd sagemaker
python train_model.py
python deploy_endpoint.py

# Deploy infrastructure
cd ../terraform
terraform init
terraform plan
terraform apply

# Test API endpoint
curl -X POST https://your-api-gateway-url/predict \
  -H "Content-Type: application/json" \
  -d '{"headcount": 150, "avg_salary": 85000, "turnover_rate": 0.12}'
```

## Features

- ML-powered cost predictions
- RESTful API for real-time predictions
- Historical prediction tracking
- Interactive cost dashboards
- Serverless architecture
- Scalable and cost-efficient

## API Usage

### Prediction Endpoint

**POST** `/predict`

**Request Body:**
```json
{
  "headcount": 150,
  "avg_salary": 85000,
  "turnover_rate": 0.12,
  "department": "Engineering",
  "benefits_multiplier": 1.35
}
```

**Response:**
```json
{
  "predicted_annual_cost": 17212500,
  "confidence_interval": [16500000, 17925000],
  "prediction_id": "pred_abc123",
  "timestamp": 1703779200
}
```

## Model Details

- **Algorithm:** XGBoost Regression
- **Features:** headcount, avg_salary, turnover_rate, benefits_multiplier, department
- **Training Data:** Historical HR cost data from 2020-2025
- **Accuracy:** RMSE < 5% on validation set

## Future Enhancements

- Add scenario planning (what-if analysis)
- Incorporate external economic indicators
- Multi-year forecasting
- Integration with HRIS systems
- Advanced visualization (Tableau/Power BI)

## License

MIT

---

**Project Status:** In Development  
**Author:** Dan Larkin  
**Date:** December 2025
