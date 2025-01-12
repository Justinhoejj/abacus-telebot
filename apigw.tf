# API Gateway
resource "aws_apigatewayv2_api" "http_api" {
  name          = "my-serverless-api"
  protocol_type = "HTTP"
}

# Lambda Integration with API Gateway
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.my_lambda.arn
}

# Route for API Gateway
resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}" # Matches all HTTP methods and paths
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Deploy the API
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default" # Default stage
  auto_deploy = true
}

# Grant API Gateway permission to invoke the Lambda function
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.my_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

################### endpoint configuration for test lambda ##################
# Lambda Integration with API Gateway
resource "aws_apigatewayv2_integration" "lambda_integration_stg_endpoint" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.abacus-telebot-stg.arn
}

# Route for API Gateway
resource "aws_apigatewayv2_route" "stg_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY ${local.stg_route}" # Matches all HTTP methods and paths
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration_stg_endpoint.id}"
}

resource "aws_lambda_permission" "api_gateway_invoke_stg_endpoint" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.abacus-telebot-stg.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}