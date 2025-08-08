# ============================================================================
# SSL Module Variables
# ============================================================================

variable "domain_name" {
  description = "Domain name for the certificate"
  type        = string
}

variable "subject_alternative_names" {
  description = "Subject alternative names for the certificate"
  type        = list(string)
  default     = []
}

variable "wildcard_san_names" {
  description = "Subject alternative names for the wildcard certificate"
  type        = list(string)
  default     = []
}

variable "zone_id" {
  description = "Route53 zone ID for certificate validation"
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

variable "create_wildcard_certificate" {
  description = "Create wildcard certificate"
  type        = bool
  default     = false
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 