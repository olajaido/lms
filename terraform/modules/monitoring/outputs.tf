# ============================================================================
# Monitoring Module Outputs
# ============================================================================

output "application_log_group" {
  description = "Application log group name"
  value       = aws_cloudwatch_log_group.application.name
}

output "access_log_group" {
  description = "Access log group name"
  value       = aws_cloudwatch_log_group.access.name
}

output "error_log_group" {
  description = "Error log group name"
  value       = aws_cloudwatch_log_group.error.name
}

output "dashboard_name" {
  description = "CloudWatch dashboard name"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "dashboard_arn" {
  description = "CloudWatch dashboard ARN"
  value       = aws_cloudwatch_dashboard.main.dashboard_arn
}

output "alerts_topic_arn" {
  description = "SNS alerts topic ARN"
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_role_arn" {
  description = "CloudWatch role ARN"
  value       = aws_iam_role.cloudwatch.arn
}

output "rds_cpu_alarm_arn" {
  description = "RDS CPU alarm ARN"
  value       = aws_cloudwatch_metric_alarm.rds_cpu.arn
}

output "rds_memory_alarm_arn" {
  description = "RDS memory alarm ARN"
  value       = aws_cloudwatch_metric_alarm.rds_memory.arn
}

output "redis_cpu_alarm_arn" {
  description = "Redis CPU alarm ARN"
  value       = aws_cloudwatch_metric_alarm.redis_cpu.arn
}

output "alb_5xx_alarm_arn" {
  description = "ALB 5XX alarm ARN"
  value       = aws_cloudwatch_metric_alarm.alb_5xx.arn
}

output "eks_nodes_alarm_arn" {
  description = "EKS nodes alarm ARN"
  value       = aws_cloudwatch_metric_alarm.eks_nodes.arn
} 