# ============================================================================
# Kubernetes Ingress Module Outputs
# ============================================================================

output "api_gateway_ingress_name" {
  description = "API Gateway ingress name"
  value       = kubernetes_ingress_v1.api_gateway.metadata[0].name
}

output "user_service_ingress_name" {
  description = "User service ingress name"
  value       = kubernetes_ingress_v1.user_service.metadata[0].name
}

output "course_service_ingress_name" {
  description = "Course service ingress name"
  value       = kubernetes_ingress_v1.course_service.metadata[0].name
}

output "content_service_ingress_name" {
  description = "Content service ingress name"
  value       = kubernetes_ingress_v1.content_service.metadata[0].name
}

output "assessment_service_ingress_name" {
  description = "Assessment service ingress name"
  value       = kubernetes_ingress_v1.assessment_service.metadata[0].name
}

output "enrollment_service_ingress_name" {
  description = "Enrollment service ingress name"
  value       = kubernetes_ingress_v1.enrollment_service.metadata[0].name
}

output "progress_service_ingress_name" {
  description = "Progress service ingress name"
  value       = kubernetes_ingress_v1.progress_service.metadata[0].name
}

output "communication_service_ingress_name" {
  description = "Communication service ingress name"
  value       = kubernetes_ingress_v1.communication_service.metadata[0].name
}

output "analytics_service_ingress_name" {
  description = "Analytics service ingress name"
  value       = kubernetes_ingress_v1.analytics_service.metadata[0].name
} 