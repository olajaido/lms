# ============================================================================
# Monitoring Module Variables
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

variable "log_retention_days" {
  description = "Log retention days"
  type        = number
  default     = 30
}

variable "rds_instance_id" {
  description = "RDS instance ID"
  type        = string
}

variable "redis_cluster_id" {
  description = "Redis cluster ID"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ALB ARN suffix"
  type        = string
}

variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "rds_cpu_threshold" {
  description = "RDS CPU threshold"
  type        = number
  default     = 80
}

variable "rds_memory_threshold" {
  description = "RDS memory threshold"
  type        = number
  default     = 1000000000  # 1GB in bytes
}

variable "redis_cpu_threshold" {
  description = "Redis CPU threshold"
  type        = number
  default     = 80
}

variable "alb_5xx_threshold" {
  description = "ALB 5XX threshold"
  type        = number
  default     = 10
}

variable "eks_node_threshold" {
  description = "EKS node threshold"
  type        = number
  default     = 2
}

variable "alarm_email" {
  description = "Email for alarm notifications"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 