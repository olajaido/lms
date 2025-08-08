# ============================================================================
# SSL Module - Custom Implementation
# ============================================================================

# ============================================================================
# ACM CERTIFICATE
# ============================================================================

resource "aws_acm_certificate" "main" {
  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-cert"
  })
}

# ============================================================================
# CERTIFICATE VALIDATION
# ============================================================================

# resource "aws_route53_record" "cert_validation" {
#   for_each = {
#     for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
#       name   = dvo.resource_record_name
#       record = dvo.resource_record_value
#       type   = dvo.resource_record_type
#     }
#   }

#   allow_overwrite = true
#   name            = each.value.name
#   records         = [each.value.record]
#   ttl             = 60
#   type            = each.value.type
#   zone_id         = var.zone_id
# }

# resource "aws_acm_certificate_validation" "main" {
#   certificate_arn         = aws_acm_certificate.main.arn
#   validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
# }

# ============================================================================
# WILDCARD CERTIFICATE (if needed)
# ============================================================================

resource "aws_acm_certificate" "wildcard" {
  count = var.create_wildcard_certificate ? 1 : 0

  domain_name               = "*.${var.domain_name}"
  subject_alternative_names = var.wildcard_san_names
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-wildcard-cert"
  })
}

# Wildcard certificate validation
resource "aws_route53_record" "wildcard_cert_validation" {
  for_each = var.create_wildcard_certificate ? {
    for dvo in aws_acm_certificate.wildcard[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.zone_id
}

resource "aws_acm_certificate_validation" "wildcard" {
  count = var.create_wildcard_certificate ? 1 : 0

  certificate_arn         = aws_acm_certificate.wildcard[0].arn
  validation_record_fqdns = [for record in aws_route53_record.wildcard_cert_validation[0] : record.fqdn]
}

# ============================================================================
# CERTIFICATE MANAGER POLICY
# ============================================================================

resource "aws_iam_policy" "certificate_manager" {
  name        = "${var.project_name}-certificate-manager-${var.environment}"
  description = "Policy for certificate management"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "acm:DescribeCertificate",
          "acm:GetCertificate",
          "acm:ListCertificates",
          "acm:RequestCertificate",
          "acm:DeleteCertificate",
          "acm:ImportCertificate",
          "acm:AddTagsToCertificate",
          "acm:RemoveTagsFromCertificate",
          "acm:UpdateCertificateOptions"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-certificate-manager-${var.environment}"
  })
}

# ============================================================================
# CERTIFICATE EXPORT POLICY
# ============================================================================

resource "aws_iam_policy" "certificate_export" {
  name        = "${var.project_name}-certificate-export-${var.environment}"
  description = "Policy for certificate export"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "acm:ExportCertificate",
          "acm:GetCertificate"
        ]
        Resource = [
          aws_acm_certificate.main.arn
        ]
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-certificate-export-${var.environment}"
  })
} 