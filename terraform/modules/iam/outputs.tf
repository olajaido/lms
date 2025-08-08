# ============================================================================
# IAM Module Outputs
# ============================================================================

output "cluster_autoscaler_role_arn" {
  description = "Cluster autoscaler role ARN"
  value       = aws_iam_role.cluster_autoscaler.arn
}

output "lms_services_role_arn" {
  description = "LMS services role ARN"
  value       = aws_iam_role.lms_services.arn
}

output "eks_node_group_role_arn" {
  description = "EKS node group role ARN"
  value       = aws_iam_role.eks_node_group.arn
}

output "eks_cluster_role_arn" {
  description = "EKS cluster role ARN"
  value       = aws_iam_role.eks_cluster.arn
}

output "backup_role_arn" {
  description = "Backup role ARN"
  value       = aws_iam_role.backup.arn
}

output "monitoring_role_arn" {
  description = "Monitoring role ARN"
  value       = aws_iam_role.monitoring.arn
}

output "cluster_autoscaler_role_name" {
  description = "Cluster autoscaler role name"
  value       = aws_iam_role.cluster_autoscaler.name
}

output "lms_services_role_name" {
  description = "LMS services role name"
  value       = aws_iam_role.lms_services.name
}

output "eks_node_group_role_name" {
  description = "EKS node group role name"
  value       = aws_iam_role.eks_node_group.name
}

output "eks_cluster_role_name" {
  description = "EKS cluster role name"
  value       = aws_iam_role.eks_cluster.name
} 