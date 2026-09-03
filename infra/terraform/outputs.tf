# ==============================================================================
# Outputs - Datos que Terraform nos devuelve después de crear la infraestructura
# ==============================================================================
# Estos valores son los que necesitaremos para:
#   - Conectarnos por SSH a la instancia
#   - Configurar Chef para apuntar a la IP del servidor
#   - Que los scripts suban datos al bucket correcto

output "instance_public_ip" {
  description = "IP pública de la instancia EC2 (para SSH y configuración con Chef)"
  value       = aws_instance.agent_runner.public_ip
}

output "instance_id" {
  description = "ID de la instancia EC2 en AWS"
  value       = aws_instance.agent_runner.id
}

output "s3_bucket_name" {
  description = "Nombre del bucket S3 donde se guardan los JSON de los agentes"
  value       = aws_s3_bucket.agent_data.id
}

output "s3_bucket_arn" {
  description = "ARN del bucket S3 (identificador único en AWS)"
  value       = aws_s3_bucket.agent_data.arn
}

output "iam_role_arn" {
  description = "ARN del rol IAM asignado a la instancia"
  value       = aws_iam_role.agent_runner_role.arn
}
