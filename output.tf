output "api_endpoint_prd" {
  value = "${aws_apigatewayv2_api.http_api.api_endpoint}${local.prd_route}"
}

output "api_endpoint_stg" {
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}${local.stg_route}"
  description = "The API Gateway endpoint URL for the staging handler"
}