# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_basic_execution" {
  name       = "lambda-basic-execution"
  roles      = [aws_iam_role.lambda_exec_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Create a custom policy for DynamoDB access (Read and Write)
resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name        = "lambda-dynamodb-policy"
  description = "Policy granting Lambda read/write access to DynamoDB"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:GetItem"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:dynamodb:ap-southeast-1:*:table/abacus-ledger",
          "arn:aws:dynamodb:ap-southeast-1:*:table/abacus-user-meta"]
      }
    ]
  })
}

# Attach the DynamoDB policy to the Lambda execution role
resource "aws_iam_policy_attachment" "lambda_dynamodb_execution" {
  name       = "lambda-dynamodb-execution"
  roles      = [aws_iam_role.lambda_exec_role.name]
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}

# Create ZIP file using archive_file
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src" # Path to your Lambda source folder
  output_path = "${path.module}/out/lambda_function_1201.zip"
}

# Lambda function
resource "aws_lambda_function" "my_lambda" {
  function_name = "abacus-telebot"
  role          = aws_iam_role.lambda_exec_role.arn
  runtime       = "python3.9" # Replace with your desired runtime
  handler       = "index.lambda_handler"
  filename      = data.archive_file.lambda_zip.output_path
  timeout       = 30

  # Environment variables (if any)
  environment {
    variables = {
      TELEGRAM_BOT_TOKEN = var.bot_token
    }
  }
}

# Lambda function
resource "aws_lambda_function" "abacus-telebot-stg" {
  function_name = "abacus-telebot-stg"
  role          = aws_iam_role.lambda_exec_role.arn
  runtime       = "python3.9" # Replace with your desired runtime
  handler       = "index.lambda_handler"
  filename      = data.archive_file.lambda_zip.output_path
  timeout       = 30

  # Environment variables (if any)
  environment {
    variables = {
      TELEGRAM_BOT_TOKEN = var.bot_token_test
    }
  }
}