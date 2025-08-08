# ============================================================================
# Kubernetes Ingress Module Variables
# ============================================================================

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 