# ==============================================================================
# Infraestructura Principal 
# Proyecto: Sistema Multiagentes - Turismo Médico
# ==============================================================================
# Este archivo define los recursos de AWS que necesita el sistema:
#   1. Una instancia EC2 donde corren los agentes (scrapers de Python + Playwright)
#   2. Un bucket S3 para almacenar los JSON generados por los agentes
#   3. Reglas de red (Security Group) para acceso controlado
#   4. Un rol IAM para que la EC2 pueda escribir al bucket S3
# ==============================================================================

# --- Proveedor de AWS ---
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Team        = "equipo-charlie"
    }
  }
}

# ==============================================================================
# 1. ALMACENAMIENTO - Bucket S3 para los JSON de los agentes
# ==============================================================================
# Aquí se guardan los archivos doctor_data.json, hotel_data.json, etc.
# Cada ejecución del scraper sube su resultado al bucket.

resource "aws_s3_bucket" "agent_data" {
  bucket = "${var.project_name}-${var.environment}-agent-data"

  tags = {
    Description = "Almacenamiento de datos JSON generados por los agentes scrapers"
  }
}

# Versionado: conserva un historial de cada archivo subido.
# Si un scraper genera datos corruptos, podemos recuperar la versión anterior.
resource "aws_s3_bucket_versioning" "agent_data_versioning" {
  bucket = aws_s3_bucket.agent_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Bloquear acceso público al bucket (los datos son internos).
resource "aws_s3_bucket_public_access_block" "agent_data_public_access" {
  bucket = aws_s3_bucket.agent_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ==============================================================================
# 2. RED - Security Group (Firewall) para la instancia EC2
# ==============================================================================
# Controla qué tráfico puede entrar y salir de la máquina.

resource "aws_security_group" "agent_runner_sg" {
  name        = "${var.project_name}-${var.environment}-agent-sg"
  description = "Reglas de firewall para la instancia que corre los agentes"

  # Permitir SSH (puerto 22) solo para administración remota.
  # IMPORTANTE: En producción, restringir cidr_blocks a tu IP fija.
  ingress {
    description = "SSH para administracion"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # TODO: Restringir a la IP del equipo en producción
  }

  # Permitir todo el tráfico de salida (necesario para que los scrapers
  # puedan conectarse a Doctoralia, APIs de hoteles, etc.)
  egress {
    description = "Permitir todo trafico de salida"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-agent-sg"
  }
}

# ==============================================================================
# 3. PERMISOS IAM - Rol para que la EC2 acceda al bucket S3
# ==============================================================================
# Sin este rol, la instancia EC2 no tendría permiso de subir archivos a S3.

# Política de confianza: "quién puede usar este rol" → las instancias EC2
resource "aws_iam_role" "agent_runner_role" {
  name = "${var.project_name}-${var.environment}-agent-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Description = "Rol IAM para la instancia EC2 que ejecuta los agentes"
  }
}

# Política de permisos: "qué puede hacer este rol" → leer/escribir en el bucket S3
resource "aws_iam_role_policy" "agent_s3_access" {
  name = "${var.project_name}-${var.environment}-s3-access"
  role = aws_iam_role.agent_runner_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          aws_s3_bucket.agent_data.arn,
          "${aws_s3_bucket.agent_data.arn}/*"
        ]
      }
    ]
  })
}

# Instance Profile: el "puente" que conecta el rol IAM con la instancia EC2
resource "aws_iam_instance_profile" "agent_runner_profile" {
  name = "${var.project_name}-${var.environment}-agent-profile"
  role = aws_iam_role.agent_runner_role.name
}

# ==============================================================================
# 4. CÓMPUTO - Instancia EC2 para ejecutar los agentes
# ==============================================================================
# Seleccionar la AMI más reciente de Ubuntu 22.04 LTS en la región elegida.
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # ID oficial de Canonical (Ubuntu)

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "agent_runner" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.agent_runner_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.agent_runner_profile.name

  # Disco de 8 GB gp2 (Free Tier incluye hasta 30 GB de EBS gp2)
  root_block_device {
    volume_size = 8
    volume_type = "gp2" # gp2 está incluido en Free Tier (gp3 NO)
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-agent-runner"
    Description = "Servidor principal para ejecutar agentes scrapers del sistema multiagentes"
  }
}
