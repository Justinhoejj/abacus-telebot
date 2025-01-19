variable "bot_token" {
  type      = string
  sensitive = true
}

variable "abacus_version" {
  type        = string
  description = "When changesa ready for deployment, version bump will trigger deployment of source code"
}

variable "bot_token_test" {
  type      = string
  sensitive = true
}