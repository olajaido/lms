# ============================================================================
# DNS Module Variables
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

variable "alb_dns_name" {
  description = "ALB DNS name"
  type        = string
}

variable "alb_zone_id" {
  description = "ALB zone ID"
  type        = string
}

variable "secondary_alb_dns_name" {
  description = "Secondary ALB DNS name for failover"
  type        = string
  default     = null
}

variable "secondary_alb_zone_id" {
  description = "Secondary ALB zone ID for failover"
  type        = string
  default     = null
}

variable "enable_mx_records" {
  description = "Enable MX records"
  type        = bool
  default     = false
}

variable "enable_spf_record" {
  description = "Enable SPF record"
  type        = bool
  default     = false
}

variable "enable_dmarc_record" {
  description = "Enable DMARC record"
  type        = bool
  default     = false
}

variable "enable_health_checks" {
  description = "Enable health checks"
  type        = bool
  default     = false
}

variable "enable_failover" {
  description = "Enable failover routing"
  type        = bool
  default     = false
}

variable "ns_delegations" {
  description = "NS delegations for subdomains"
  type        = map(list(string))
  default     = {}
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 