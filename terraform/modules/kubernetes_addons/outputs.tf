# ============================================================================
# Kubernetes Addons Module Outputs
# ============================================================================

output "cluster_autoscaler_status" {
  description = "Cluster autoscaler status"
  value       = helm_release.cluster_autoscaler.status
}

output "metrics_server_status" {
  description = "Metrics server status"
  value       = helm_release.metrics_server.status
}

output "ingress_nginx_status" {
  description = "Ingress nginx status"
  value       = helm_release.ingress_nginx.status
}

output "prometheus_status" {
  description = "Prometheus status"
  value       = var.enable_prometheus ? helm_release.prometheus[0].status : null
}

output "grafana_status" {
  description = "Grafana status"
  value       = var.enable_grafana ? helm_release.grafana[0].status : null
}

output "cert_manager_status" {
  description = "Cert-manager status"
  value       = var.enable_cert_manager ? helm_release.cert_manager[0].status : null
}

output "fluentd_status" {
  description = "Fluentd status"
  value       = var.enable_fluentd ? helm_release.fluentd[0].status : null
}

output "cluster_autoscaler_namespace" {
  description = "Cluster autoscaler namespace"
  value       = helm_release.cluster_autoscaler.namespace
}

output "metrics_server_namespace" {
  description = "Metrics server namespace"
  value       = helm_release.metrics_server.namespace
}

output "ingress_nginx_namespace" {
  description = "Ingress nginx namespace"
  value       = helm_release.ingress_nginx.namespace
}

output "prometheus_namespace" {
  description = "Prometheus namespace"
  value       = var.enable_prometheus ? helm_release.prometheus[0].namespace : null
}

output "grafana_namespace" {
  description = "Grafana namespace"
  value       = var.enable_grafana ? helm_release.grafana[0].namespace : null
}

output "cert_manager_namespace" {
  description = "Cert-manager namespace"
  value       = var.enable_cert_manager ? helm_release.cert_manager[0].namespace : null
}

output "fluentd_namespace" {
  description = "Fluentd namespace"
  value       = var.enable_fluentd ? helm_release.fluentd[0].namespace : null
} 