

output "bucket_name" {
  value       = google_storage_bucket.bucket.name
  description = "Name of the bucket"
}

output "bucket_url" {
  value       = google_storage_bucket.bucket.url
  description = "URL of the bucket"
}

output "db_instance_name" {
  value       = module.sql-db.instance_name
  description = "The name for Cloud SQL instance"
}

output "db_instance_self_link" {
  value       = module.sql-db.instance_self_link
  description = "The URI of the master instance"
}

output "db_instance_connection_name" {
  value       = module.sql-db.instance_connection_name
  description = "The connection name of the master instance to be used in connection strings"
}

output "db_public_ip_address" {
  value       = module.sql-db.public_ip_address
  description = "The first public (PRIMARY) IPv4 address assigned for the master instance"
}

output "pubsub_topic" {
  value       = length(google_pubsub_topic.topic) > 0 ? google_pubsub_topic.topic.0.name : ""
  description = "The name of the Pub/Sub topic"
}

output "pubsub_subscriptor" {
  value       = google_pubsub_subscription.migsc-push-subs.name
  description = "Pubsub subsciptor name"
}

output "sa_appl" {
  value       = data.google_app_engine_default_service_account.default.email
  description = "Service Account for the migscaler appl"
}

output "iam_role_appl" {
  value       = google_project_iam_custom_role.waverunner.role_id
  description = "IAM Role for migscaler appl"
}

# output "application_url" {
#   value = "https://${var.site_domain_name}"
#   description = "application URL"
# }
