# ============================================================================
# ALB Module Outputs
# ============================================================================

output "alb_id" {
  description = "Application Load Balancer ID"
  value       = aws_lb.main.id
}

output "alb_arn" {
  description = "Application Load Balancer ARN"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Application Load Balancer zone ID"
  value       = aws_lb.main.zone_id
}

output "alb_arn_suffix" {
  description = "Application Load Balancer ARN suffix"
  value       = aws_lb.main.arn_suffix
}

output "security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

output "frontend_target_group_arn" {
  description = "Frontend target group ARN"
  value       = aws_lb_target_group.frontend.arn
}

output "api_gateway_target_group_arn" {
  description = "API Gateway target group ARN"
  value       = aws_lb_target_group.api_gateway.arn
}

output "http_listener_arn" {
  description = "HTTP listener ARN"
  value       = aws_lb_listener.http.arn
}

output "https_listener_arn" {
  description = "HTTPS listener ARN"
  value       = aws_lb_listener.https.arn
}

output "access_logs_bucket" {
  description = "ALB access logs bucket"
  value       = var.enable_access_logs ? aws_s3_bucket.alb_logs[0].bucket : null
} 