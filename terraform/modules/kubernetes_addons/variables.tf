# ============================================================================
# Kubernetes Addons Module Variables
# ============================================================================

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "cluster_autoscaler_role_arn" {
  description = "Cluster autoscaler role ARN"
  type        = string
}

variable "cluster_dependency" {
  description = "Cluster dependency"
  type        = any
}

variable "cluster_autoscaler_version" {
  description = "Cluster autoscaler version"
  type        = string
  default     = "9.35.0"
}

variable "metrics_server_version" {
  description = "Metrics server version"
  type        = string
  default     = "3.12.2"
}

variable "ingress_nginx_version" {
  description = "Ingress nginx version"
  type        = string
  default     = "4.7.1"
}

variable "enable_prometheus" {
  description = "Enable Prometheus"
  type        = bool
  default     = true
}

variable "prometheus_version" {
  description = "Prometheus version"
  type        = string
  default     = "25.8.0"
}

variable "enable_grafana" {
  description = "Enable Grafana"
  type        = bool
  default     = true
}

variable "grafana_version" {
  description = "Grafana version"
  type        = string
  default     = "8.0.2"
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
  default     = "admin123"
}

variable "enable_cert_manager" {
  description = "Enable cert-manager"
  type        = bool
  default     = true
}

variable "cert_manager_version" {
  description = "Cert-manager version"
  type        = string
  default     = "1.13.3"
}

variable "enable_fluentd" {
  description = "Enable Fluentd"
  type        = bool
  default     = true
}

variable "fluentd_version" {
  description = "Fluentd version"
  type        = string
  default     = "0.4.4"
}

variable "elasticsearch_host" {
  description = "Elasticsearch host"
  type        = string
  default     = ""
}

variable "elasticsearch_port" {
  description = "Elasticsearch port"
  type        = string
  default     = "9200"
}

variable "elasticsearch_scheme" {
  description = "Elasticsearch scheme"
  type        = string
  default     = "http"
}

variable "elasticsearch_user" {
  description = "Elasticsearch user"
  type        = string
  default     = ""
}

variable "elasticsearch_password" {
  description = "Elasticsearch password"
  type        = string
  sensitive   = true
  default     = ""
} 