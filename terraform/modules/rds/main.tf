# ============================================================================
# RDS Module - Custom Implementation
# ============================================================================

# ============================================================================
# SUBNET GROUP
# ============================================================================

resource "aws_db_subnet_group" "main" {
  name       = "${var.identifier}-subnet-group"
  subnet_ids = var.subnet_ids
  
  tags = merge(var.common_tags, {
    Name = "${var.identifier}-subnet-group"
  })
}

# ============================================================================
# PARAMETER GROUP
# ============================================================================

resource "aws_db_parameter_group" "main" {
  family = "${var.engine}${var.engine_version}"
  name   = "${var.identifier}-parameter-group"
  
  dynamic "parameter" {
    for_each = var.parameters
    content {
      name  = parameter.value.name
      value = parameter.value.value
    }
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.identifier}-parameter-group"
  })
}

# ============================================================================
# OPTION GROUP
# ============================================================================

resource "aws_db_option_group" "main" {
  count = var.create_option_group ? 1 : 0
  
  engine_name          = var.engine
  major_engine_version = var.engine_version
  
  name = "${var.identifier}-option-group"
  
  tags = merge(var.common_tags, {
    Name = "${var.identifier}-option-group"
  })
}

# ============================================================================
# SECURITY GROUP
# ============================================================================

resource "aws_security_group" "rds" {
  name_prefix = "${var.identifier}-rds-"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = var.port
    to_port         = var.port
    protocol        = "tcp"
    security_groups = var.allowed_security_group_ids
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.identifier}-rds-sg"
  })
}

# ============================================================================
# RDS INSTANCE
# ============================================================================

resource "aws_db_instance" "main" {
  identifier = var.identifier
  
  # Engine configuration
  engine               = var.engine
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  
  # Storage configuration
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type         = var.storage_type
  storage_encrypted    = var.storage_encrypted
  kms_key_id          = var.kms_key_id
  
  # Database configuration
  db_name  = var.db_name
  username = var.username
  password = var.password
  port     = var.port
  
  # Network configuration
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  copy_tags_to_snapshot = var.copy_tags_to_snapshot
  
  # Maintenance configuration
  maintenance_window = var.maintenance_window
  
  # Monitoring configuration
  monitoring_interval = var.monitoring_interval
  monitoring_role_arn = var.monitoring_role_arn
  
  # Performance Insights
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_retention_period
  
  # Deletion protection
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot
  
  # Final snapshot configuration
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.identifier}-final-snapshot"
  
  # Parameter group
  parameter_group_name = aws_db_parameter_group.main.name
  
  # Option group
  option_group_name = var.create_option_group ? aws_db_option_group.main[0].name : null
  
  # Multi-AZ configuration
  multi_az = var.multi_az
  
  # Public accessibility
  publicly_accessible = var.publicly_accessible
  
  # Auto minor version upgrade
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  
  # Apply immediately
  apply_immediately = var.apply_immediately
  
  tags = merge(var.common_tags, {
    Name = "${var.identifier}-db"
  })
}

# ============================================================================
# DATABASE SCHEMAS
# ============================================================================

# 
# resource "kubernetes_job" "create_schemas" {
#   metadata {
#     name      = "create-schemas"
#     namespace = "default"
#   }
  
#   spec {
#     template {
#       metadata {}
#       spec {
#         container {
#           name  = "postgres-setup"
#           image = "postgres:15"
#           command = ["psql"]
#           args = [
#             "-h", aws_db_instance.main.address,
#             "-p", "5432",
#             "-U", var.username,
#             "-d", var.db_name,
#             "-c", <<-EOT
#               CREATE SCHEMA IF NOT EXISTS user_service;
#               CREATE SCHEMA IF NOT EXISTS course_service;
#               CREATE SCHEMA IF NOT EXISTS enrollment_service;
#               CREATE SCHEMA IF NOT EXISTS content_service;
#               CREATE SCHEMA IF NOT EXISTS assessment_service;
#               CREATE SCHEMA IF NOT EXISTS progress_service;
#               CREATE SCHEMA IF NOT EXISTS communication_service;
#               CREATE SCHEMA IF NOT EXISTS analytics_service;
              
#               -- Grant permissions to each schema
#               GRANT ALL PRIVILEGES ON SCHEMA user_service TO ${var.username};
#               GRANT ALL PRIVILEGES ON SCHEMA course_service TO ${var.username};
#               GRANT ALL PRIVILEGES ON SCHEMA enrollment_service TO ${var.username};
#               GRANT ALL PRIVILEGES ON SCHEMA content_service TO ${var.username};
#               GRANT ALL PRIVILEGES ON SCHEMA assessment_service TO ${var.username};
#               GRANT ALL PRIVILEGES ON SCHEMA progress_service TO ${var.username};
#               GRANT ALL PRIVILEGES ON SCHEMA communication_service TO ${var.username};
#               GRANT ALL PRIVILEGES ON SCHEMA analytics_service TO ${var.username};
#             EOT
#           ]
          
#           env {
#             name  = "PGPASSWORD"
#             value = var.password
#           }
#         }
#         restart_policy = "Never"
#       }
#     }
#   }
  
#   depends_on = [aws_db_instance.main]
# }

#Create schemas for each microservice
# resource "null_resource" "create_schemas" {
#   triggers = {
#     db_instance_id = aws_db_instance.main.id
#   }

#   provisioner "local-exec" {
#     command = <<-EOT
#       PGPASSWORD=${var.password} psql \
#         -h ${aws_db_instance.main.address} \
#         -p ${aws_db_instance.main.port} \
#         -U ${var.username} \
#         -d ${var.db_name} \
#         -c "
#         CREATE SCHEMA IF NOT EXISTS user_service;
#         CREATE SCHEMA IF NOT EXISTS course_service;
#         CREATE SCHEMA IF NOT EXISTS enrollment_service;
#         CREATE SCHEMA IF NOT EXISTS content_service;
#         CREATE SCHEMA IF NOT EXISTS assessment_service;
#         CREATE SCHEMA IF NOT EXISTS progress_service;
#         CREATE SCHEMA IF NOT EXISTS communication_service;
#         CREATE SCHEMA IF NOT EXISTS analytics_service;
        
#         -- Grant permissions to each schema
#         GRANT ALL PRIVILEGES ON SCHEMA user_service TO ${var.username};
#         GRANT ALL PRIVILEGES ON SCHEMA course_service TO ${var.username};
#         GRANT ALL PRIVILEGES ON SCHEMA enrollment_service TO ${var.username};
#         GRANT ALL PRIVILEGES ON SCHEMA content_service TO ${var.username};
#         GRANT ALL PRIVILEGES ON SCHEMA assessment_service TO ${var.username};
#         GRANT ALL PRIVILEGES ON SCHEMA progress_service TO ${var.username};
#         GRANT ALL PRIVILEGES ON SCHEMA communication_service TO ${var.username};
#         GRANT ALL PRIVILEGES ON SCHEMA analytics_service TO ${var.username};
#       "
#     EOT
#   }

#   depends_on = [aws_db_instance.main]
# }

# ============================================================================
# READ REPLICA (if enabled)
# ============================================================================

resource "aws_db_instance" "read_replica" {
  count = var.create_read_replica ? 1 : 0
  
  identifier = "${var.identifier}-read-replica"
  
  # Source instance
  replicate_source_db = aws_db_instance.main.identifier
  
  # Engine configuration
  engine               = var.engine
  engine_version       = var.engine_version
  instance_class       = var.read_replica_instance_class
  
  # Storage configuration
  allocated_storage     = var.read_replica_allocated_storage
  storage_type         = var.storage_type
  storage_encrypted    = var.storage_encrypted
  kms_key_id          = var.kms_key_id
  
  # Network configuration
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  # Monitoring configuration
  monitoring_interval = var.monitoring_interval
  monitoring_role_arn = var.monitoring_role_arn
  
  # Performance Insights
  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_retention_period
  
  # Deletion protection
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot
  
  # Final snapshot configuration
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.identifier}-read-replica-final-snapshot"
  
  # Public accessibility
  publicly_accessible = var.publicly_accessible
  
  # Auto minor version upgrade
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  
  # Apply immediately
  apply_immediately = var.apply_immediately
  
  tags = merge(var.common_tags, {
    Name = "${var.identifier}-read-replica"
  })
}

# ============================================================================
# CLOUDWATCH LOG GROUP
# ============================================================================

resource "aws_cloudwatch_log_group" "rds" {
  count = var.enable_cloudwatch_logs ? 1 : 0
  
  name              = "/aws/rds/instance/${var.identifier}"
  retention_in_days = var.cloudwatch_logs_retention_days
  
  tags = merge(var.common_tags, {
    Name = "${var.identifier}-logs"
  })
}

# ============================================================================
# IAM ROLE FOR ENHANCED MONITORING
# ============================================================================

resource "aws_iam_role" "rds_monitoring" {
  count = var.monitoring_interval > 0 ? 1 : 0
  
  name = "${var.identifier}-rds-monitoring-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(var.common_tags, {
    Name = "${var.identifier}-rds-monitoring-role"
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.monitoring_interval > 0 ? 1 : 0
  
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
} 