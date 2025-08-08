# ============================================================================
# DNS Module - Custom Implementation
# ============================================================================

# ============================================================================
# HOSTED ZONE
# ============================================================================

resource "aws_route53_zone" "main" {
  name = var.domain_name

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-zone"
  })
}

# ============================================================================
# A RECORDS
# ============================================================================

# Frontend A record (main application)
resource "aws_route53_record" "frontend" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# API subdomain A record
resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# Admin subdomain A record
resource "aws_route53_record" "admin" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "admin.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# ============================================================================
# CNAME RECORDS
# ============================================================================

# www subdomain CNAME record
resource "aws_route53_record" "www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "CNAME"
  ttl     = "300"
  records = [var.domain_name]
}

# ============================================================================
# MX RECORDS
# ============================================================================

# Mail exchange records
resource "aws_route53_record" "mx" {
  count = var.enable_mx_records ? 1 : 0
  
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "MX"
  ttl     = "300"

  records = [
    "10 mail.${var.domain_name}."
  ]
}

# ============================================================================
# TXT RECORDS
# ============================================================================

# SPF record for email authentication
resource "aws_route53_record" "spf" {
  count = var.enable_spf_record ? 1 : 0
  
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "TXT"
  ttl     = "300"

  records = [
    "v=spf1 include:_spf.google.com ~all"
  ]
}

# DMARC record
resource "aws_route53_record" "dmarc" {
  count = var.enable_dmarc_record ? 1 : 0
  
  zone_id = aws_route53_zone.main.zone_id
  name    = "_dmarc.${var.domain_name}"
  type    = "TXT"
  ttl     = "300"

  records = [
    "v=DMARC1; p=quarantine; rua=mailto:dmarc@${var.domain_name}"
  ]
}

# ============================================================================
# NS RECORDS (DELEGATION)
# ============================================================================

# NS records for subdomain delegation (if needed)
resource "aws_route53_record" "ns_delegation" {
  for_each = var.ns_delegations

  zone_id = aws_route53_zone.main.zone_id
  name    = each.key
  type    = "NS"
  ttl     = "300"
  records = each.value
}

# ============================================================================
# HEALTH CHECKS
# ============================================================================

# Health check for the main application
resource "aws_route53_health_check" "app" {
  count = var.enable_health_checks ? 1 : 0
  
  fqdn              = var.domain_name
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = "3"
  request_interval  = "30"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-health-check"
  })
}

# ============================================================================
# FAILOVER RECORDS (if needed)
# ============================================================================

# Primary A record for failover
resource "aws_route53_record" "app_primary" {
  count = var.enable_failover ? 1 : 0
  
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }

  set_identifier = "primary"
  health_check_id = aws_route53_health_check.app[0].id

  failover_routing_policy {
    type = "PRIMARY"
  }
}

# Secondary A record for failover
resource "aws_route53_record" "app_secondary" {
  count = var.enable_failover ? 1 : 0
  
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.secondary_alb_dns_name
    zone_id                = var.secondary_alb_zone_id
    evaluate_target_health = true
  }

  set_identifier = "secondary"
  health_check_id = aws_route53_health_check.app[0].id

  failover_routing_policy {
    type = "SECONDARY"
  }
} 