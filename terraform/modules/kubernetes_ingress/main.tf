# ============================================================================
# Kubernetes Ingress Module - Custom Implementation
# ============================================================================

# ============================================================================
# FRONTEND INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "frontend" {
  metadata {
    name      = "frontend-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = var.domain_name
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = "frontend-service"
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# API GATEWAY INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "api_gateway" {
  metadata {
    name      = "api-gateway-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = "api-gateway-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# USER SERVICE INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "user_service" {
  metadata {
    name      = "user-service-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/api/users"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/api/users"
          path_type = "Prefix"
          backend {
            service {
              name = "user-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# COURSE SERVICE INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "course_service" {
  metadata {
    name      = "course-service-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/api/courses"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/api/courses"
          path_type = "Prefix"
          backend {
            service {
              name = "course-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# CONTENT SERVICE INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "content_service" {
  metadata {
    name      = "content-service-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/api/content"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "100m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/api/content"
          path_type = "Prefix"
          backend {
            service {
              name = "content-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# ASSESSMENT SERVICE INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "assessment_service" {
  metadata {
    name      = "assessment-service-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/api/assessments"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/api/assessments"
          path_type = "Prefix"
          backend {
            service {
              name = "assessment-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# ENROLLMENT SERVICE INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "enrollment_service" {
  metadata {
    name      = "enrollment-service-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/api/enrollments"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/api/enrollments"
          path_type = "Prefix"
          backend {
            service {
              name = "enrollment-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# PROGRESS SERVICE INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "progress_service" {
  metadata {
    name      = "progress-service-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/api/progress"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/api/progress"
          path_type = "Prefix"
          backend {
            service {
              name = "progress-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# COMMUNICATION SERVICE INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "communication_service" {
  metadata {
    name      = "communication-service-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/api/communications"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/api/communications"
          path_type = "Prefix"
          backend {
            service {
              name = "communication-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# ============================================================================
# ANALYTICS SERVICE INGRESS
# ============================================================================

resource "kubernetes_ingress_v1" "analytics_service" {
  metadata {
    name      = "analytics-service-ingress"
    namespace = "default"
    annotations = {
      "kubernetes.io/ingress.class"                    = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/api/analytics"
      "nginx.ingress.kubernetes.io/ssl-redirect"       = "false"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "50m"
      "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
      "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
    }
  }

  spec {
    rule {
      host = "api.${var.domain_name}"
      http {
        path {
          path      = "/api/analytics"
          path_type = "Prefix"
          backend {
            service {
              name = "analytics-service"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
} 