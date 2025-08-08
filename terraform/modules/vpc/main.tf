# ============================================================================
# VPC Module - Custom Implementation
# ============================================================================

# ============================================================================
# VPC
# ============================================================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-vpc"
  })
}

# ============================================================================
# INTERNET GATEWAY
# ============================================================================

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-igw"
  })
}

# ============================================================================
# PUBLIC SUBNETS
# ============================================================================

resource "aws_subnet" "public" {
  count             = length(var.public_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnets[count.index]
  availability_zone = var.availability_zones[count.index]
  
  map_public_ip_on_launch = true
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-public-subnet-${count.index + 1}"
    "kubernetes.io/role/elb" = "1"
  })
}

# ============================================================================
# PRIVATE SUBNETS
# ============================================================================

resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = var.availability_zones[count.index]
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-private-subnet-${count.index + 1}"
    "kubernetes.io/role/internal-elb" = "1"
  })
}

# ============================================================================
# ELASTIC IPs FOR NAT GATEWAYS
# ============================================================================

resource "aws_eip" "nat" {
  count  = length(var.public_subnets)
  domain = "vpc"
  
  depends_on = [aws_internet_gateway.main]
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-nat-eip-${count.index + 1}"
  })
}

# ============================================================================
# NAT GATEWAYS
# ============================================================================

resource "aws_nat_gateway" "main" {
  count         = length(var.public_subnets)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  depends_on = [aws_internet_gateway.main]
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-nat-gateway-${count.index + 1}"
  })
}

# ============================================================================
# ROUTE TABLES
# ============================================================================

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-public-rt"
  })
}

# Private Route Tables (one per AZ)
resource "aws_route_table" "private" {
  count  = length(var.private_subnets)
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-private-rt-${count.index + 1}"
  })
}

# ============================================================================
# ROUTE TABLE ASSOCIATIONS
# ============================================================================

# Public subnet associations
resource "aws_route_table_association" "public" {
  count          = length(var.public_subnets)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private subnet associations
resource "aws_route_table_association" "private" {
  count          = length(var.private_subnets)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# ============================================================================
# SECURITY GROUPS
# ============================================================================

# Default security group
resource "aws_security_group" "default" {
  name_prefix = "${var.project_name}-default-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    protocol  = "-1"
    self      = true
    from_port = 0
    to_port   = 0
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-default-sg"
  })
}

# ============================================================================
# VPC ENDPOINTS (for AWS services)
# ============================================================================

# S3 VPC Endpoint
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.aws_region}.s3"
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-s3-endpoint"
  })
}

# ECR VPC Endpoint
# resource "aws_vpc_endpoint" "ecr" {
#   vpc_id             = aws_vpc.main.id
#   service_name       = "com.amazonaws.${var.aws_region}.ecr.api"
#   vpc_endpoint_type  = "Interface"
#   subnet_ids         = aws_subnet.private[*].id
#   private_dns_enabled = true
  
#   security_group_ids = [aws_security_group.vpc_endpoints.id]
  
#   tags = merge(var.common_tags, {
#     Name = "${var.project_name}-ecr-endpoint"
#   })
# }

# ECR DKR VPC Endpoint
# resource "aws_vpc_endpoint" "ecr_dkr" {
#   vpc_id             = aws_vpc.main.id
#   service_name       = "com.amazonaws.${var.aws_region}.ecr.dkr"
#   vpc_endpoint_type  = "Interface"
#   subnet_ids         = aws_subnet.private[*].id
#   private_dns_enabled = true
  
#   security_group_ids = [aws_security_group.vpc_endpoints.id]
  
#   tags = merge(var.common_tags, {
#     Name = "${var.project_name}-ecr-dkr-endpoint"
#   })
# }

# CloudWatch Logs VPC Endpoint
resource "aws_vpc_endpoint" "logs" {
  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type  = "Interface"
  subnet_ids         = aws_subnet.private[*].id
  private_dns_enabled = true
  
  security_group_ids = [aws_security_group.vpc_endpoints.id]
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-logs-endpoint"
  })
}

# Security group for VPC endpoints
resource "aws_security_group" "vpc_endpoints" {
  name_prefix = "${var.project_name}-vpc-endpoints-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.default.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-vpc-endpoints-sg"
  })
} 