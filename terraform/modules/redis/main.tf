# ============================================================================
# Redis Module - Custom Implementation
# ============================================================================

# ============================================================================
# SUBNET GROUP
# ============================================================================

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.cluster_id}-subnet-group"
  subnet_ids = var.subnet_ids
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-subnet-group"
  })
}

# ============================================================================
# PARAMETER GROUP
# ============================================================================

resource "aws_elasticache_parameter_group" "main" {
  family = var.parameter_group_family
  name   = "${var.cluster_id}-parameter-group"
  
  dynamic "parameter" {
    for_each = var.parameters
    content {
      name  = parameter.value.name
      value = parameter.value.value
    }
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-parameter-group"
  })
}

# ============================================================================
# SECURITY GROUP
# ============================================================================

resource "aws_security_group" "redis" {
  name_prefix = "${var.cluster_id}-redis-"
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
    Name = "${var.cluster_id}-redis-sg"
  })
}

# ============================================================================
# REPLICATION GROUP
# ============================================================================

resource "aws_elasticache_replication_group" "main" {
  replication_group_id = var.cluster_id
  description = "Redis replication group for ${var.cluster_id}"
  
  # Engine configuration
  engine               = var.engine
  engine_version       = var.engine_version
  node_type            = var.node_type
  port                 = var.port
  
  # Network configuration
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  parameter_group_name       = aws_elasticache_parameter_group.main.name
  
  # Cluster configuration
  num_cache_clusters = var.num_cache_clusters
  automatic_failover_enabled = var.automatic_failover_enabled
  multi_az_enabled          = var.multi_az_enabled
  
  # Cache cluster configuration
  at_rest_encryption_enabled = var.at_rest_encryption_enabled
  transit_encryption_enabled = var.transit_encryption_enabled
  kms_key_id                = var.kms_key_id
  
  # Logging configuration
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis[0].name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }
  
  # Maintenance configuration
  maintenance_window = var.maintenance_window
  snapshot_window   = var.snapshot_window
  snapshot_retention_limit = var.snapshot_retention_limit
  
  # Tags
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-redis"
  })
}

# ============================================================================
# CLOUDWATCH LOG GROUP
# ============================================================================

resource "aws_cloudwatch_log_group" "redis" {
  count = var.enable_cloudwatch_logs ? 1 : 0
  
  name              = "/aws/elasticache/${var.cluster_id}"
  retention_in_days = var.cloudwatch_logs_retention_days
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-logs"
  })
}

# ============================================================================
# CLOUDWATCH ALARMS
# ============================================================================

# CPU Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "cpu_utilization" {
  count = var.enable_cloudwatch_alarms ? 1 : 0
  
  alarm_name          = "${var.cluster_id}-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = var.cpu_utilization_threshold
  alarm_description   = "Redis cluster CPU utilization is too high"
  
  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-cpu-alarm"
  })
}

# Memory Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "memory_utilization" {
  count = var.enable_cloudwatch_alarms ? 1 : 0
  
  alarm_name          = "${var.cluster_id}-memory-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = var.memory_utilization_threshold
  alarm_description   = "Redis cluster memory utilization is too high"
  
  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-memory-alarm"
  })
}

# Connection Count Alarm
resource "aws_cloudwatch_metric_alarm" "connection_count" {
  count = var.enable_cloudwatch_alarms ? 1 : 0
  
  alarm_name          = "${var.cluster_id}-connection-count"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CurrConnections"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = var.connection_count_threshold
  alarm_description   = "Redis cluster connection count is too high"
  
  dimensions = {
    CacheClusterId = aws_elasticache_replication_group.main.id
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-connection-alarm"
  })
}

# ============================================================================
# SNS TOPIC FOR ALARMS
# ============================================================================

resource "aws_sns_topic" "redis_alarms" {
  count = var.enable_cloudwatch_alarms && var.sns_topic_arn == null ? 1 : 0
  
  name = "${var.cluster_id}-redis-alarms"
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-redis-alarms-topic"
  })
}

# SNS Topic Subscription
resource "aws_sns_topic_subscription" "redis_alarms" {
  count = var.enable_cloudwatch_alarms ? 1 : 0
  
  topic_arn = var.sns_topic_arn != null ? var.sns_topic_arn : aws_sns_topic.redis_alarms[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# ============================================================================
# IAM ROLE FOR CLOUDWATCH LOGS
# ============================================================================

resource "aws_iam_role" "elasticache_logs" {
  count = var.enable_cloudwatch_logs ? 1 : 0
  
  name = "${var.cluster_id}-elasticache-logs-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "elasticache.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(var.common_tags, {
    Name = "${var.cluster_id}-elasticache-logs-role"
  })
}

resource "aws_iam_role_policy" "elasticache_logs" {
  count = var.enable_cloudwatch_logs ? 1 : 0
  
  name = "${var.cluster_id}-elasticache-logs-policy"
  role = aws_iam_role.elasticache_logs[0].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      }
    ]
  })
} 