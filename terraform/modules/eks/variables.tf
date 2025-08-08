# ============================================================================
# EKS Module Variables
# ============================================================================

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.31"
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the EKS cluster"
  type        = list(string)
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

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 