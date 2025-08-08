# ============================================================================
# IAM Module Variables
# ============================================================================

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "s3_content_bucket_arn" {
  description = "S3 content bucket ARN"
  type        = string
}

variable "s3_backup_bucket_arn" {
  description = "S3 backup bucket ARN"
  type        = string
}

variable "rds_resource_id" {
  description = "RDS resource ID"
  type        = string
}

variable "rds_username" {
  description = "RDS username"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 