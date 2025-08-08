# ============================================================================
# LMS Platform - Terraform Infrastructure
# ============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  
  backend "s3" {
    bucket = "lms-platform-terraform-state"
    key    = "lms-platform/terraform.tfstate"
    region = "eu-west-2"
  }
}

# ============================================================================
# PROVIDERS
# ============================================================================

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "lms-platform"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

# ============================================================================
# DATA SOURCES
# ============================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
}

data "aws_caller_identity" "current" {}

data "aws_route53_zone" "main" {
  name = "lms.j3consult.co.uk"
  private_zone = false
}

# ============================================================================
# VPC MODULE
# ============================================================================

module "vpc" {
  source = "./modules/vpc"
  
  vpc_cidr = var.vpc_cidr
  public_subnets = var.public_subnets
  private_subnets = var.private_subnets
  availability_zones = data.aws_availability_zones.available.names
  aws_region = var.aws_region
  project_name = var.project_name
  environment = var.environment
  common_tags = var.common_tags
}

# ============================================================================
# EKS CLUSTER MODULE
# ============================================================================

module "eks" {
  source = "./modules/eks"
  
  cluster_name = "${var.project_name}-cluster"
  kubernetes_version = var.kubernetes_version
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  
  node_group_desired_capacity = var.node_group_desired_capacity
  node_group_max_capacity = var.node_group_max_capacity
  node_group_min_capacity = var.node_group_min_capacity
  node_group_instance_types = var.node_group_instance_types

  
  enable_spot_nodes = var.enable_spot_nodes
  spot_node_group_desired_capacity = var.spot_node_group_desired_capacity
  spot_node_group_max_capacity = var.spot_node_group_max_capacity
  spot_node_group_min_capacity = var.spot_node_group_min_capacity
  spot_node_group_instance_types = var.spot_node_group_instance_types
  
  environment = var.environment
  project_name = var.project_name
  common_tags = var.common_tags
}

# ============================================================================
# RDS DATABASE MODULE
# ============================================================================

module "rds" {
  source = "./modules/rds"
  
  identifier = "${var.project_name}-db"
  engine = "postgres"
  engine_version = "15"
  instance_class = var.rds_instance_class
  allocated_storage = var.rds_allocated_storage
  storage_encrypted = true
  storage_type = "gp3"
  
  db_name = "lms_db"
  username = var.rds_username
  password = var.rds_password
  port = 5432
  
  subnet_ids = module.vpc.private_subnet_ids
  vpc_id = module.vpc.vpc_id
  allowed_security_group_ids = [module.eks.cluster_security_group_id, module.eks.node_security_group_id]
  
  backup_retention_period = var.rds_backup_retention_period
  backup_window = "03:00-06:00"
  maintenance_window = "Mon:00:00-Mon:03:00"
  
  deletion_protection = var.environment == "production"
  skip_final_snapshot = false
  
  multi_az = var.environment == "production"
  publicly_accessible = false
  
  monitoring_interval =0
  performance_insights_enabled = var.environment == "production"
  
  parameters = [
    {
      name  = "autovacuum"
      value = "1"
    },
    {
      name  = "client_encoding"
      value = "utf8"
    },
    {
      name  = "timezone"
      value = "UTC"
    }
  ]
  
  common_tags = var.common_tags
}

# ============================================================================
# REDIS CACHE MODULE
# ============================================================================

module "redis" {
  source = "./modules/redis"
  
  cluster_id = "${var.project_name}-redis"
  engine = "redis"
  engine_version = "7.0"
  node_type = var.redis_node_type
  port = 6379
  
  subnet_ids = module.vpc.private_subnet_ids
  vpc_id = module.vpc.vpc_id
  allowed_security_group_ids = [module.eks.cluster_security_group_id]
  
  parameter_group_family = "redis7"
  num_cache_clusters = var.environment == "production" ? 2 : 1
  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled = var.environment == "production"
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  maintenance_window = "sun:23:00-mon:01:00"
  snapshot_window = "01:00-03:00"
  snapshot_retention_limit = var.environment == "production" ? 7 : 3
  
  enable_cloudwatch_logs = true
  cloudwatch_logs_retention_days = 7
  
  enable_cloudwatch_alarms = true
  cpu_utilization_threshold = 80
  memory_utilization_threshold = 80
  connection_count_threshold = 1000
  alarm_email = var.alarm_email
  
  parameters = [
    {
      name  = "maxmemory-policy"
      value = "allkeys-lru"
    },
    {
      name  = "notify-keyspace-events"
      value = "Ex"
    }
  ]
  
  common_tags = var.common_tags
}

# ============================================================================
# LOAD BALANCER MODULE
# ============================================================================

module "alb" {
  source = "./modules/alb"
  
  name = "${var.project_name}-alb"
  vpc_id = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  environment = var.environment
  project_name = var.project_name
  common_tags = var.common_tags
  certificate_arn = module.ssl.certificate_arn
}

# ============================================================================
# S3 STORAGE MODULE
# ============================================================================

module "s3" {
  source = "./modules/s3"
  
  project_name = var.project_name
  environment = var.environment
  common_tags = var.common_tags
}

# ============================================================================
# DNS MODULE
# ============================================================================

module "dns" {
  source = "./modules/dns"
  
  domain_name = var.domain_name
  project_name = var.project_name
  environment = var.environment
  alb_dns_name = module.alb.alb_dns_name
  alb_zone_id = module.alb.alb_zone_id
  common_tags = var.common_tags
}

# ============================================================================
# SSL CERTIFICATE MODULE
# ============================================================================

module "ssl" {
  source = "./modules/ssl"
  
  domain_name = var.domain_name
  zone_id = data.aws_route53_zone.main.zone_id
  project_name = var.project_name
  environment = var.environment
  common_tags = var.common_tags
}

# ============================================================================
# MONITORING MODULE
# ============================================================================

module "monitoring" {
  source = "./modules/monitoring"
  
  project_name = var.project_name
  environment = var.environment
  aws_region = var.aws_region
  rds_instance_id = module.rds.db_instance_id
  redis_cluster_id = module.redis.replication_group_id
  alb_arn_suffix = module.alb.alb_arn_suffix
  eks_cluster_name = module.eks.cluster_name
  alarm_email = var.alarm_email
  common_tags = var.common_tags
}

# ============================================================================
# IAM MODULE
# ============================================================================

module "iam" {
  source = "./modules/iam"
  
  project_name = var.project_name
  environment = var.environment
  aws_region = var.aws_region
  account_id = data.aws_caller_identity.current.account_id
  s3_content_bucket_arn = module.s3.content_bucket_arn
  s3_backup_bucket_arn = module.s3.backups_bucket_arn
  rds_resource_id = module.rds.db_instance_id
  rds_username = var.rds_username
  common_tags = var.common_tags
}

# ============================================================================
# KUBERNETES ADDONS MODULE
# ============================================================================

module "kubernetes_addons" {
  source = "./modules/kubernetes_addons"
  
  cluster_name = module.eks.cluster_name
  aws_region = var.aws_region
  cluster_autoscaler_role_arn = module.iam.cluster_autoscaler_role_arn
  cluster_dependency = module.eks.cluster_id
  grafana_admin_password = var.grafana_admin_password
  elasticsearch_user = var.elasticsearch_user
  elasticsearch_password = var.elasticsearch_password
}

# ============================================================================
# KUBERNETES INGRESS MODULE
# ============================================================================

module "kubernetes_ingress" {
  source = "./modules/kubernetes_ingress"
  
  domain_name = var.domain_name
  project_name = var.project_name
  environment = var.environment
  common_tags = var.common_tags
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = module.eks.cluster_certificate_authority_data
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "public_subnets" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.db_instance_endpoint
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.redis.primary_endpoint_address
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.alb.alb_dns_name
}

output "domain_name" {
  description = "Domain name"
  value       = var.domain_name
}

output "certificate_arn" {
  description = "ACM certificate ARN"
  value       = module.ssl.certificate_arn
}

output "content_storage_bucket" {
  description = "S3 content storage bucket name"
  value       = module.s3.content_bucket
}

output "backup_bucket" {
  description = "S3 backup bucket name"
  value       = module.s3.backups_bucket
} 