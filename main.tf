# Define the backend configuration
terraform {
  backend "s3" {
    bucket         = "terraform-state-store-020125"  # Replace with your S3 bucket name
    key            = "abacus-telebot/terraform.tfstate" # State file path
    region         = "ap-southeast-1"                  # Replace with your AWS region
    encrypt        = true                         # Enable state file encryption
  }
}

# Provider configuration
provider "aws" {
  region = "ap-southeast-1" # Replace with your preferred AWS region
}