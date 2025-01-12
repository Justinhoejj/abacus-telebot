output "api_endpoint" {
  value = aws_apigatewayv2_stage.default_stage.invoke_url
}

output "api_endpoint_stg" {
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}${local.stg_route}"
  description = "The API Gateway endpoint URL for the staging handler"
}