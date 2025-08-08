# ============================================================================
# RDS Module Outputs
# ============================================================================

output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.main.arn
}

output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_address" {
  description = "RDS instance address"
  value       = aws_db_instance.main.address
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "db_instance_status" {
  description = "RDS instance status"
  value       = aws_db_instance.main.status
}

output "db_subnet_group_name" {
  description = "RDS subnet group name"
  value       = aws_db_subnet_group.main.name
}

output "db_parameter_group_name" {
  description = "RDS parameter group name"
  value       = aws_db_parameter_group.main.name
}

output "db_option_group_name" {
  description = "RDS option group name"
  value       = var.create_option_group ? aws_db_option_group.main[0].name : null
}

output "db_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}

output "read_replica_endpoint" {
  description = "Read replica endpoint"
  value       = var.create_read_replica ? aws_db_instance.read_replica[0].endpoint : null
}

output "read_replica_address" {
  description = "Read replica address"
  value       = var.create_read_replica ? aws_db_instance.read_replica[0].address : null
}

output "monitoring_role_arn" {
  description = "Monitoring role ARN"
  value       = var.monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null
} 