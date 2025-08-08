# ============================================================================
# LMS Platform - Terraform Variables
# ============================================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "lms-platform"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "lms.j3consult.co.uk"
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
  default     = "admin123"
}

variable "alarm_email" {
  description = "Email for alarm notifications"
  type        = string
  default     = "adeluwoyeolajide@yahoo.com"
}

# ============================================================================
# VPC & NETWORKING
# ============================================================================

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# ============================================================================
# EKS CLUSTER
# ============================================================================

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.31"
}

variable "node_group_desired_capacity" {
  description = "Desired capacity for general node group"
  type        = number
  default     = 2
}

variable "node_group_max_capacity" {
  description = "Maximum capacity for general node group"
  type        = number
  default     = 5
}

variable "node_group_min_capacity" {
  description = "Minimum capacity for general node group"
  type        = number
  default     = 1
}

variable "node_group_instance_types" {
  description = "Instance types for general node group"
  type        = list(string)
  default     = ["t3.medium", "t3.large"]
}

variable "enable_spot_nodes" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = true
}

variable "spot_node_group_desired_capacity" {
  description = "Desired capacity for spot node group"
  type        = number
  default     = 1
}

variable "spot_node_group_max_capacity" {
  description = "Maximum capacity for spot node group"
  type        = number
  default     = 3
}

variable "spot_node_group_min_capacity" {
  description = "Minimum capacity for spot node group"
  type        = number
  default     = 0
}

variable "spot_node_group_instance_types" {
  description = "Instance types for spot node group"
  type        = list(string)
  default     = ["t3.medium", "t3.large", "t3.xlarge"]
}

variable "elasticsearch_user" {
  description = "Elasticsearch username"
  type        = string
  default     = "elastic"
}

variable "elasticsearch_password" {
  description = "Elasticsearch password"
  type        = string
  sensitive   = true
  default     = "elastic123"
}

# ============================================================================
# RDS DATABASE
# ============================================================================

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "rds_username" {
  description = "RDS master username"
  type        = string
  default     = "lms_admin"
  sensitive   = true
}

variable "rds_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
  default     = "lms_admin123"
}

variable "rds_backup_retention_period" {
  description = "RDS backup retention period in days"
  type        = number
  default     = 7
}

# ============================================================================
# REDIS
# ============================================================================

variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

# ============================================================================
# TAGS
# ============================================================================

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "lms-platform"
    ManagedBy   = "terraform"
    Environment = "production"
  }
} 