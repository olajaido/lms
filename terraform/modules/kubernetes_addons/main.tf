# ============================================================================
# Kubernetes Addons Module - Custom Implementation
# ============================================================================

# ============================================================================
# CLUSTER AUTOSCALER
# ============================================================================

resource "helm_release" "cluster_autoscaler" {
  name       = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart      = "cluster-autoscaler"
  namespace  = "kube-system"
  version    = var.cluster_autoscaler_version

  set {
    name  = "autoDiscovery.clusterName"
    value = var.cluster_name
  }

  set {
    name  = "awsRegion"
    value = var.aws_region
  }

  set {
    name  = "rbac.serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = var.cluster_autoscaler_role_arn
  }

  set {
    name  = "extraArgs.scale-down-enabled"
    value = "true"
  }

  set {
    name  = "extraArgs.scale-down-delay-after-add"
    value = "10m"
  }

  set {
    name  = "extraArgs.scale-down-delay-after-delete"
    value = "10s"
  }

  set {
    name  = "extraArgs.scale-down-delay-after-failure"
    value = "3m"
  }

  set {
    name  = "extraArgs.scale-down-unneeded-time"
    value = "10m"
  }

  depends_on = [var.cluster_dependency]
}

# ============================================================================
# METRICS SERVER
# ============================================================================

resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = var.metrics_server_version

  set {
    name  = "args[0]"
    value = "--kubelet-insecure-tls"
  }

  set {
    name  = "args[1]"
    value = "--kubelet-preferred-address-types=InternalIP"
  }

  depends_on = [var.cluster_dependency]
}

# ============================================================================
# INGRESS NGINX
# ============================================================================

resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = "ingress-nginx"
  version    = var.ingress_nginx_version
  create_namespace = true

  # Use ClusterIP for internal service routing (ALB handles external traffic)
  set {
    name  = "controller.service.type"
    value = "ClusterIP"
  }

  # Enable internal load balancing
  set {
    name  = "controller.service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-internal"
    value = "true"
  }

  # Configure for internal use
  set {
    name  = "controller.ingressClassResource.name"
    value = "nginx"
  }

  set {
    name  = "controller.ingressClassResource.default"
    value = "true"
  }

  # Resource limits
  set {
    name  = "controller.resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "controller.resources.requests.memory"
    value = "128Mi"
  }

  set {
    name  = "controller.resources.limits.cpu"
    value = "500m"
  }

  set {
    name  = "controller.resources.limits.memory"
    value = "512Mi"
  }

  # Enable metrics for monitoring
  set {
    name  = "controller.metrics.enabled"
    value = "true"
  }

  # Configure for microservices
  set {
    name  = "controller.config.enable-real-ip"
    value = "true"
  }

  set {
    name  = "controller.config.use-proxy-protocol"
    value = "false"
  }

  depends_on = [var.cluster_dependency]
}

# ============================================================================
# PROMETHEUS
# ============================================================================

resource "helm_release" "prometheus" {
  count      = var.enable_prometheus ? 1 : 0
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "prometheus"
  namespace  = "monitoring"
  version    = var.prometheus_version
  create_namespace = true

  set {
    name  = "server.persistentVolume.enabled"
    value = "true"
  }

  set {
    name  = "server.persistentVolume.size"
    value = "10Gi"
  }

  set {
    name  = "server.resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "server.resources.requests.memory"
    value = "256Mi"
  }

  set {
    name  = "server.resources.limits.cpu"
    value = "500m"
  }

  set {
    name  = "server.resources.limits.memory"
    value = "1Gi"
  }

  depends_on = [var.cluster_dependency]
}

# ============================================================================
# GRAFANA
# ============================================================================

resource "helm_release" "grafana" {
  count      = var.enable_grafana ? 1 : 0
  name       = "grafana"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "grafana"
  namespace  = "monitoring"
  version    = var.grafana_version
  create_namespace = true

  set {
    name  = "adminPassword"
    value = var.grafana_admin_password
  }

  set {
    name  = "persistence.enabled"
    value = "true"
  }

  set {
    name  = "persistence.size"
    value = "10Gi"
  }

  set {
    name  = "resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "resources.requests.memory"
    value = "256Mi"
  }

  set {
    name  = "resources.limits.cpu"
    value = "500m"
  }

  set {
    name  = "resources.limits.memory"
    value = "1Gi"
  }

  set {
    name  = "service.type"
    value = "ClusterIP"
  }

  depends_on = [var.cluster_dependency]
}

# ============================================================================
# CERT-MANAGER
# ============================================================================

resource "helm_release" "cert_manager" {
  count      = var.enable_cert_manager ? 1 : 0
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  namespace  = "cert-manager"
  version    = var.cert_manager_version
  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }

  set {
    name  = "global.leaderElection.namespace"
    value = "cert-manager"
  }

  depends_on = [var.cluster_dependency]
}

# ============================================================================
# FLUENTD
# ============================================================================

# resource "helm_release" "fluentd" {
#   count      = var.enable_fluentd ? 1 : 0
#   name       = "fluentd"
#   repository = "https://fluent.github.io/helm-charts"
#   chart      = "fluentd"
#   namespace  = "logging"
#   version    = var.fluentd_version
#   create_namespace = true

#   set {
#     name  = "elasticsearch.host"
#     value = "elasticsearch-master"
#   }

#   set {
#     name  = "elasticsearch.port"
#     value = "9200"
#   }

#   set {
#     name  = "elasticsearch.scheme"
#     value = "http"
#   }

#   set {
#     name  = "elasticsearch.user"
#     value = var.elasticsearch_user
#   }

#   set {
#     name  = "elasticsearch.password"
#     value = var.elasticsearch_password
#   }
#   set {
#     name  = "metrics.enabled"            
#     value = "true"
#   }
#   set {
#     name  = "metrics.service.port"       
#     value = "24231"
#   }

#   values = [
#     yamlencode({
#       livenessProbe = {
#         enabled = false
#       }
#       readinessProbe = {
#         enabled = false
#       }
#       # Also disable startup probe if it exists
#       startupProbe = {
#         enabled = false
#       }
#     })
#   ]
#     name  = "metrics.enabled"
#     value = "true"
#   }
#   set {
#     name  = "metrics.port"
#     value = "24231"
#   }
#   set {
#     name  = "metrics.path"
#     value = "/metrics"
#   }
#   set {
#     name  = "livenessProbe.enabled"
#     value = "true"
#   }
#   set {
#     name  = "livenessProbe.httpGet.path"
#     value = "/metrics"
#   }
#   set {
#     name  = "livenessProbe.httpGet.port"
#     value = "24231"
#   }
#   set {
#     name  = "readinessProbe.enabled"
#     value = "true"
#   }
#   set {
#     name  = "readinessProbe.httpGet.path"
#     value = "/metrics"
#   }
#   set {
#     name  = "readinessProbe.httpGet.port"
#     value = "24231"
#   }
#   set {
#   name  = "daemonset.containerPorts.metrics.enabled"
#   value = "true"
# }
# set {
#   name  = "daemonset.containerPorts.metrics.port"
#   value = "24231"
# }
# set {
#   name  = "daemonset.containerPorts.metrics.name"
#   value = "metrics"
# }

# set {
#   name  = "livenessProbe.httpGet.port"
#   value = "metrics"
# }
# set {
#   name  = "readinessProbe.httpGet.port"
#   value = "metrics"
# }
resource "helm_release" "fluentd" {
  count            = var.enable_fluentd ? 1 : 0
  name             = "fluentd"
  repository       = "https://fluent.github.io/helm-charts"
  chart            = "fluentd"
  namespace        = "logging"
  version          = var.fluentd_version
  create_namespace = true

  # --- ES target (keep your values) ---
  set { 
    name = "elasticsearch.host"   
    value = "elasticsearch-master" 
    }
  set { 
    name = "elasticsearch.port"   
    value = "9200" 
    }
  set { 
    name = "elasticsearch.scheme" 
    value = "http" 
    }
  set { 
    name = "elasticsearch.user"   
    value = var.elasticsearch_user 
    }
  set { 
    name = "elasticsearch.password" 
    value = var.elasticsearch_password 
    }

  # --- Metrics wiring ---
  set { 
    name = "metrics.enabled"       
    value = "true" 
    }
  set { 
    name = "metrics.port"          
    value = "24231" 
    }   
  set { 
    name = "metrics.path"          
    value = "/metrics" 
    }

  # Expose a named container port "metrics"
  set { 
    name = "daemonset.containerPorts.metrics.enabled" 
    value = "true" 
    }
  set { 
    name = "daemonset.containerPorts.metrics.name"   
    value = "metrics" 
    }
  set { 
    name = "daemonset.containerPorts.metrics.port"    
    value = "24231" 
    }
  values = [
    yamlencode({
      livenessProbe  = null
      readinessProbe = null
    })
  ]  

  # Make probes point to the named port/path
  # set { 
  #   name = "daemonset.livenessProbe.enabled"           
  #   value = "true" 
  #   }
  # set { 
  #   name = "daemonset.livenessProbe.httpGet.path"      
  #   value = "/metrics" 
  #   }
  # set { 
  #   name = "daemonset.livenessProbe.httpGet.port"      
  #   value = "metrics" 
  #   }

  # set { 
  #   name = "daemonset.readinessProbe.enabled"          
  #   value = "true" 
  #   }
  # set { 
  #   name = "daemonset.readinessProbe.httpGet.path"     
  #   value = "/metrics" 
  #   }
  # set { 
  #   name = "daemonset.readinessProbe.httpGet.port"     
  #   value = "metrics" 
  #   }
 

  # Optional: give Helm more time to settle
  wait    = true
  timeout = 900
  atomic  = true

  depends_on = [var.cluster_dependency]
}

# resource "helm_release" "fluentd" {
#   count             = var.enable_fluentd ? 1 : 0
#   name              = "fluentd"
#   repository        = "https://fluent.github.io/helm-charts"
#   chart             = "fluentd"
#   namespace         = "logging"
#   version           = var.fluentd_version
#   create_namespace  = true

#   set { 
#     name = "elasticsearch.host"    
#     value = "elasticsearch-master" 
#     }
#   set { 
#     name = "elasticsearch.port"    
#     value = "9200" 
#     }
#   set { 
#     name = "elasticsearch.scheme"  
#     value = "http" 
#     }
#   set { 
#     name = "elasticsearch.user"    
#     value = var.elasticsearch_user 
#     }
#   set { 
#     name = "elasticsearch.password" 
#     value = var.elasticsearch_password 
#     }

#   set { 
#     name = "metrics.enabled"       
#     value = "true" 
#     }
#   set { 
#     name = "metrics.port"          
#     value = "24231" 
#     }
#   set { 
#     name = "metrics.path"          
#     value = "/metrics" 
#     }

#   # expose a named containerPort so probes can refer to it
#   set { 
#     name = "daemonset.containerPorts.metrics.enabled" 
#     value = "true" 
#     }
#   set { 
#     name = "daemonset.containerPorts.metrics.port"    
#     value = "24231" 
#     }
#   set { 
#     name = "daemonset.containerPorts.metrics.name"    
#     value = "metrics" 
#     }

#   # liveness/readiness by name
#   set { 
#     name = "livenessProbe.enabled"              
#     value = "true" 
#     }
#   set { 
#     name = "livenessProbe.httpGet.path"         
#     value = "/metrics" 
#     }
#   set { 
#     name = "livenessProbe.httpGet.port"         
#     value = "metrics" 
#     }

#   set { 
#     name = "readinessProbe.enabled"             
#     value = "true" 
#     }
#   set { 
#     name = "readinessProbe.httpGet.path"        
#     value = "/metrics" 
#     }
#   set { 
#     name = "readinessProbe.httpGet.port"        
#     value = "metrics" 
#     }

#   depends_on = [var.cluster_dependency]
# }


resource "helm_release" "elasticsearch" {
  name              = "elasticsearch"
  repository        = "https://helm.elastic.co"
  chart             = "elasticsearch"
  namespace         = "logging"
  create_namespace  = false
  version           = "7.17.3"             

  set {
    name  = "service.type"
    value = "ClusterIP"
  }

  # adjust replicas, storage, resources, etc. as needed
  set {
    name  = "replicas"
    value = "1"
  }
}
