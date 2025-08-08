# ============================================================================
# DNS Module Outputs
# ============================================================================

output "zone_id" {
  description = "Route53 hosted zone ID"
  value       = aws_route53_zone.main.zone_id
}

output "name_servers" {
  description = "Name servers for the hosted zone"
  value       = aws_route53_zone.main.name_servers
}

output "zone_arn" {
  description = "Route53 hosted zone ARN"
  value       = aws_route53_zone.main.arn
}

output "frontend_record_name" {
  description = "Frontend record name"
  value       = aws_route53_record.frontend.name
}

output "api_record_name" {
  description = "API record name"
  value       = aws_route53_record.api.name
}

output "admin_record_name" {
  description = "Admin record name"
  value       = aws_route53_record.admin.name
}

output "www_record_name" {
  description = "WWW record name"
  value       = aws_route53_record.www.name
}

output "health_check_id" {
  description = "Health check ID"
  value       = var.enable_health_checks ? aws_route53_health_check.app[0].id : null
} 