# ============================================================================
# S3 Module Outputs
# ============================================================================

# output "terraform_state_bucket" {
#   description = "Terraform state bucket name"
#   value       = aws_s3_bucket.terraform_state.bucket
# }

# output "terraform_state_bucket_arn" {
#   description = "Terraform state bucket ARN"
#   value       = aws_s3_bucket.terraform_state.arn
# }

output "backups_bucket" {
  description = "Backups bucket name"
  value       = aws_s3_bucket.backups.bucket
}

output "backups_bucket_arn" {
  description = "Backups bucket ARN"
  value       = aws_s3_bucket.backups.arn
}

output "content_bucket" {
  description = "Content bucket name"
  value       = aws_s3_bucket.content.bucket
}

output "content_bucket_arn" {
  description = "Content bucket ARN"
  value       = aws_s3_bucket.content.arn
}

output "logs_bucket" {
  description = "Logs bucket name"
  value       = aws_s3_bucket.logs.bucket
}

output "logs_bucket_arn" {
  description = "Logs bucket ARN"
  value       = aws_s3_bucket.logs.arn
}

output "content_access_policy_arn" {
  description = "Content access policy ARN"
  value       = aws_iam_policy.content_access.arn
}

output "backup_access_policy_arn" {
  description = "Backup access policy ARN"
  value       = aws_iam_policy.backup_access.arn
} 