# ==============================================================================
# Variables de entrada para la infraestructura
# ==============================================================================
# Estas variables permiten reutilizar el mismo código para distintos entornos
# (dev, staging, prod) sin modificar la lógica principal.

variable "aws_region" {
  description = "Región de AWS donde se despliega la infraestructura"
  type        = string
  default     = "us-east-1" 
}

variable "project_name" {
  description = "Nombre del proyecto, se usa como prefijo para nombrar recursos"
  type        = string
  default     = "turismo-medico-multiagent"
}

variable "environment" {
  description = "Ambiente de despliegue (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "Tipo de instancia EC2 - t2.micro = FREE TIER (1 vCPU, 1GB RAM, 750 hrs/mes gratis)"
  type        = string
  default     = "t2.micro" # GRATIS bajo AWS Free Tier / AWS Educate
}

variable "key_pair_name" {
  description = "Nombre del Key Pair de AWS para acceso SSH a la instancia"
  type        = string
  default     = "multiagent-keypair"
}
