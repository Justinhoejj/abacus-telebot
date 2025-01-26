# Lambda function
resource "aws_lambda_function" "abacus-telebot-stg" {
  function_name    = "abacus-telebot-stg"
  role             = aws_iam_role.lambda_exec_role.arn
  runtime          = "python3.11" # Replace with your desired runtime
  handler          = "index.lambda_handler"
  filename         = data.archive_file.lambda_src_zip_stg.output_path
  source_code_hash = data.archive_file.lambda_src_zip_stg.output_md5
  timeout          = 10

  environment {
    variables = {
      TELEGRAM_BOT_TOKEN = var.bot_token_test
    }
  }


  layers = [aws_lambda_layer_version.lambda_layer_stg.arn]
}

data "archive_file" "lambda_src_zip_stg" {
  type        = "zip"
  source_dir  = "${path.module}/src" # Path to your Lambda source folder
  output_path = "${path.module}/out/lambda_src_stg.zip"
  excludes    = ["layers"]
}

data "archive_file" "lambda_layer_zip_stg" {
  type        = "zip"
  source_dir  = "${path.module}/src/layers"
  output_path = "${path.module}/out/layers_stg.zip"
}

resource "aws_lambda_layer_version" "lambda_layer_stg" {
  filename   = data.archive_file.lambda_layer_zip_stg.output_path
  layer_name = "abacus-lambda-layer-stg"

  compatible_runtimes = ["python3.11"]
}

resource "terraform_data" "register_web_token_stg" {
  triggers_replace = [aws_apigatewayv2_api.http_api.api_endpoint, local.stg_route, var.bot_token_test]
  provisioner "local-exec" {
    command     = "bash ./register_telebot.sh"
    working_dir = path.module
    environment = {
      TOKEN   = nonsensitive(var.bot_token_test)
      API_URL = "${aws_apigatewayv2_api.http_api.api_endpoint}${local.stg_route}"
    }

    on_failure = fail
  }
}