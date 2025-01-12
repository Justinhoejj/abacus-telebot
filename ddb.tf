resource "aws_dynamodb_table" "expenses_table" {
  name         = "abacus-ledger"              # Table name
  billing_mode = "PAY_PER_REQUEST"            # On-demand billing (no need to specify capacity)

  # Primary Key: Partition Key (username) and Sort Key (month_year)
  hash_key  = "username"                      # Partition key
  range_key = "year_month"                    # Sort key

  # Attribute definitions
  attribute {
    name = "username"
    type = "S"                                # String type
  }

  attribute {
    name = "year_month"
    type = "S"                                # String type (e.g., "2023-01")
  }
}
