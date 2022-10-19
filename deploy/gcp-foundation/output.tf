
//
//
// OUTPUT Values
//
//

output "bucket_name" {
  value       = module.gcp-foundation.bucket_name
  description = "Name of the bucket"
}

output "bucket_url" {
  value       = module.gcp-foundation.bucket_url
  description = "URL of the bucket"
}

# output "cloudrun_id" {
#   value       = module.gcp-foundation.cloudrun_id
#   description = "ID of the cloudrun service"
# }

# output "cloudrun_url" {
#   value       = module.gcp-foundation.cloudrun_url
#   description = "URL of the cloudrun service"
# }

output "db_instance_name" {
  value       = module.gcp-foundation.db_instance_name
  description = "The name for Cloud SQL instance"
}

output "db_instance_self_link" {
  value       = module.gcp-foundation.db_instance_self_link
  description = "The URI of the master instance"
}

output "db_instance_connection_name" {
  value       = module.gcp-foundation.db_instance_connection_name
  description = "The connection name of the master instance to be used in connection strings"
}

output "db_public_ip_address" {
  value       = module.gcp-foundation.db_public_ip_address
  description = "The first public (PRIMARY) IPv4 address assigned for the master instance"
}

output "pubsub_topic" {
  value       = module.gcp-foundation.pubsub_topic
  description = "The name of the Pub/Sub topic"
}

output "pubsub_subscriptor" {
  value       = module.gcp-foundation.pubsub_subscriptor
  description = "Pubsub subsciptor name"
}

output "service_account_appl" {
  value       = module.gcp-foundation.sa_appl
  description = "Service Account for the migscaler appl"
}

output "iam_role_appl" {
  value       = module.gcp-foundation.iam_role_appl
  description = "IAM Role for migscaler appl"
}

# output "application_url" {
#   value       = module.gcp-foundation.application_url
#   description = "Application URL"
# }
