# ============================================================================
# SSL Module Outputs
# ============================================================================

output "certificate_arn" {
  description = "Main certificate ARN"
  value       = aws_acm_certificate.main.arn
}

output "certificate_domain_name" {
  description = "Main certificate domain name"
  value       = aws_acm_certificate.main.domain_name
}

output "certificate_status" {
  description = "Main certificate status"
  value       = aws_acm_certificate.main.status
}

output "certificate_validation_arn" {
  description = "Certificate validation ARN"
  value       = aws_acm_certificate.main.arn
}

output "wildcard_certificate_arn" {
  description = "Wildcard certificate ARN"
  value       = var.create_wildcard_certificate ? aws_acm_certificate.wildcard[0].arn : null
}

output "wildcard_certificate_status" {
  description = "Wildcard certificate status"
  value       = var.create_wildcard_certificate ? aws_acm_certificate.wildcard[0].status : null
}

output "wildcard_certificate_validation_arn" {
  description = "Wildcard certificate validation ARN"
  value       = var.create_wildcard_certificate ? aws_acm_certificate_validation.wildcard[0].certificate_arn : null
}

output "certificate_manager_policy_arn" {
  description = "Certificate manager policy ARN"
  value       = aws_iam_policy.certificate_manager.arn
}

output "certificate_export_policy_arn" {
  description = "Certificate export policy ARN"
  value       = aws_iam_policy.certificate_export.arn
} 