# Single Cloud Run

The module deploys Cloud Run that communicates with Gemini APIs.

This inlcudes

- Global external application load balancer (+ Cloud Armor) -> Cloud Run -> Gemini APIs
- By default, it creates the project, it activates services and configures IAM roles.

## Deployment

```shell
# Create terraform.tfvars
cp terraform.tfvars.sample terraform.tfvars

# Customize it with your billing account and parent

# Initialize Terraform and deploy
terraform init
terraform apply

# Deploy the applicaiton: follow the commands in the output screen to deploy the application(s).
```
