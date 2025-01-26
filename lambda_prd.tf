resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "${path.module}/out/layers_0.1.zip"
  layer_name = "abacus-lambda-layer"

  compatible_runtimes = ["python3.11"]
  depends_on          = [terraform_data.release_version]
}

locals {
  prd_layer_output_path = "${path.module}/out/layers_${var.abacus_version}.zip"
  prd_src_output_path   = "${path.module}/out/lambda_src_${var.abacus_version}.zip"
}

resource "terraform_data" "replacement" {
  input = var.abacus_version
}

resource "terraform_data" "release_version" {
  lifecycle {
    replace_triggered_by = [terraform_data.replacement]
  }

  provisioner "local-exec" {
    command     = "cp $src_input $src_output; cp $layer_input $layer_output"
    working_dir = path.module
    environment = {
      src_input : data.archive_file.lambda_src_zip_stg.output_path
      src_output : local.prd_src_output_path
      layer_input : data.archive_file.lambda_layer_zip_stg.output_path
      layer_output : local.prd_layer_output_path
    }
  }
}

# Lambda function
resource "aws_lambda_function" "my_lambda" {
  function_name    = "abacus-telebot"
  role             = aws_iam_role.lambda_exec_role.arn
  runtime          = "python3.11"
  handler          = "index.lambda_handler"
  filename         = local.prd_src_output_path
  timeout          = 10
  source_code_hash = var.abacus_version
  environment {
    variables = {
      TELEGRAM_BOT_TOKEN = var.bot_token
    }
  }
  layers     = [aws_lambda_layer_version.lambda_layer.arn]
  depends_on = [terraform_data.release_version]
}

resource "terraform_data" "register_web_token" {
  triggers_replace = [aws_apigatewayv2_api.http_api.api_endpoint, local.prd_route, var.bot_token]
  provisioner "local-exec" {
    command     = "bash ./register_telebot.sh"
    working_dir = path.module
    environment = {
      TOKEN   = nonsensitive(var.bot_token)
      API_URL = "${aws_apigatewayv2_api.http_api.api_endpoint}${local.prd_route}"
    }

    on_failure = fail
  }
}