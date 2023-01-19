
data "google_project" "project" {
  project_id = var.project_id
}

resource "google_iap_brand" "project_brand" {
  support_email     = var.oauth_support_contact_email
  application_title = "${var.deployment_name} Application"
  project           = data.google_project.project.number
  depends_on        = [google_project_service.gcp_services]
}

resource "google_iap_client" "project_client" {
  display_name = "${google_iap_brand.project_brand.application_title} Client"
  brand        = google_iap_brand.project_brand.name
}




#------------------------------------------------------------------------------------
#
# Pubsub Topic and related IAM permission
#
#------------------------------------------------------------------------------------

locals {
  pubsub_svc_account_email     = "service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_pubsub_topic" "topic" {
  count        = var.create_topic ? 1 : 0
  project      = var.project_id
  name         = var.pubsub_topic
  labels       = var.gcp_labels
  kms_key_name = var.topic_kms_key_name

  dynamic "message_storage_policy" {
    for_each = var.message_storage_policy
    content {
      allowed_persistence_regions = message_storage_policy.key == "allowed_persistence_regions" ? message_storage_policy.value : null
    }
  }
}

resource "google_pubsub_topic_iam_member" "push_topic_binding" {
  for_each = var.create_topic ? { for i in var.push_subscriptions : i.name => i } : {}
  project  = var.project_id
  topic    = lookup(each.value, "dead_letter_topic", "projects/${var.project_id}/topics/${var.pubsub_topic}")
  role     = "roles/pubsub.publisher"
  member   = "serviceAccount:${local.pubsub_svc_account_email}"
  depends_on = [
    google_pubsub_topic.topic,
  ]
}


#------------------------------------------------------------------------------------
#
# Terraform module to provisioning CloudSQL (postgreSQL) DB: Instance, DB and DB user
#
#------------------------------------------------------------------------------------

# generate random password
resource "random_password" "db_user_pass" {
  length  = 16
  special = false
  upper   = true
  lower   = true
  number  = true
}

# create a secret for db user password
resource "google_secret_manager_secret" "db_user_pass" {
  project   = var.project_id
  secret_id = "migsc-db-user-pass"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.gcp_services]
}

# add secret data for password secret
resource "google_secret_manager_secret_version" "db_user_pass" {
  secret      = google_secret_manager_secret.db_user_pass.id
  secret_data = random_password.db_user_pass.result
  depends_on  = [google_project_service.gcp_services]
}

# create a secret for connection string
resource "google_secret_manager_secret" "db_conn_string" {
  project   = var.project_id
  secret_id = "migscaler-db-conn-string"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.gcp_services]
}

# add secret data for connection string secret
resource "google_secret_manager_secret_version" "db_conn_string" {
  secret      = google_secret_manager_secret.db_conn_string.id
  secret_data = "postgresql+psycopg2://${var.user_name}:${random_password.db_user_pass.result}@/${var.db_name}?host=/cloudsql/${var.project_id}:${var.region}:${module.sql-db.instance_name}"
  depends_on  = [google_project_service.gcp_services]
}

module "sql-db" {
  source                          = "GoogleCloudPlatform/sql-db/google//modules/postgresql"
  version                         = "8.0.0" # TODO: Upgrade this module to 11
  name                            = "${var.db_instance_name}-${random_string.random.result}"
  user_labels                     = var.gcp_labels
  db_name                         = var.db_name
  user_name                       = var.user_name
  user_password                   = random_password.db_user_pass.result
  database_version                = var.database_version
  project_id                      = var.project_id
  zone                            = var.zone
  region                          = var.region
  tier                            = var.tier
  maintenance_window_update_track = var.maintenance_window_update_track
  disk_size                       = var.disk_size
  maintenance_window_hour         = var.maintenance_window_hour
  ip_configuration = {
    # authorized_networks                = [{name = "network1", value = "0.0.0.0/0"},]
    authorized_networks = []
    ipv4_enabled        = true
    private_network     = ""
    require_ssl         = null
  }
  backup_configuration = {
    enabled                        = var.enable_automatic_backup
    start_time                     = var.enable_automatic_backup ? var.backup_config.start_time : null
    location                       = var.enable_automatic_backup ? var.backup_config.location : null
    point_in_time_recovery_enabled = var.enable_automatic_backup ? var.backup_config.point_in_time_recovery_enabled : false
    transaction_log_retention_days = var.enable_automatic_backup ? var.backup_config.transaction_log_retention_days : null
    retained_backups               = var.enable_automatic_backup ? var.backup_config.retained_backups : null
    retention_unit                 = var.enable_automatic_backup ? var.backup_config.retention_unit : null
  }
  activation_policy    = var.activation_policy
  availability_type    = var.availability_type
  db_charset           = var.db_charset
  db_collation         = var.db_collation
  random_instance_name = var.random_instance_name
  create_timeout       = var.create_timeout
  delete_timeout       = var.delete_timeout
  update_timeout       = var.update_timeout
  enable_default_user  = var.enable_default_user
  enable_default_db    = var.enable_default_db
  disk_type            = var.disk_type
  deletion_protection  = var.deletion_protection
}


#---------------------------------
#
# Terraform resource to create GCS
#
#---------------------------------

resource "random_string" "random" {
  length  = 5
  special = false
  upper   = false
}

resource "google_storage_bucket" "bucket" {
  name                        = "${var.bucket_name}-${random_string.random.result}"
  project                     = var.project_id
  location                    = var.region
  storage_class               = var.storage_class
  uniform_bucket_level_access = var.bucket_policy_only
  labels                      = var.gcp_labels
  force_destroy               = var.force_destroy

  versioning {
    enabled = var.versioning
  }

  dynamic "lifecycle_rule" {
    for_each = var.lifecycle_rules
    content {
      action {
        type          = lifecycle_rule.value.action.type
        storage_class = lookup(lifecycle_rule.value.action, "storage_class", null)
      }
      condition {
        age                   = lookup(lifecycle_rule.value.condition, "age", null)
        created_before        = lookup(lifecycle_rule.value.condition, "created_before", null)
        with_state            = lookup(lifecycle_rule.value.condition, "with_state", lookup(lifecycle_rule.value.condition, "is_live", false) ? "LIVE" : null)
        matches_storage_class = lookup(lifecycle_rule.value.condition, "matches_storage_class", null)
        num_newer_versions    = lookup(lifecycle_rule.value.condition, "num_newer_versions", null)
      }
    }
  }

  dynamic "logging" {
    for_each = var.log_bucket == null ? [] : [var.log_bucket]
    content {
      log_bucket        = var.log_bucket
      log_object_prefix = var.log_object_prefix
    }
  }
}

resource "google_storage_bucket_object" "gce_metadata_folder" {
  name    = "gce_metadata/"
  content = "GCE Metadata"
  bucket  = google_storage_bucket.bucket.name
}


#-----------------------------------------
#
# Terraform module to enable projects APIs
#
#-----------------------------------------

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project  = var.project_id
  service  = each.key

  timeouts {
    create = "10m"
    update = "15m"
  }

  disable_on_destroy         = false
  disable_dependent_services = true
}




//-----------------------------------------------------------------------
//
//
//  Terraform module to create Cloudrun svc and pubsub subscriptor (push)
//
//
//-----------------------------------------------------------------------

resource "google_cloud_tasks_queue" "migsc-ctq" {
  name     = "${var.cloud_tasks_queue_name}-${random_string.random.result}"
  location = var.region
  project  = var.project_id
  retry_config {
    max_attempts = 1
  }
  depends_on = [google_project_service.gcp_services]
}






//--------------------------------------------------
//
//
//  Terraform code for SA and role
//
//
//--------------------------------------------------

#
# GCP resource provisioning for custom roles and IAM permissions / Service Accounts for the BMS application
#

resource "google_project_iam_custom_role" "waverunner" {
  project     = var.project_id
  role_id     = "${var.custom_role_id}${random_string.random.result}"
  permissions = var.application_sa_custom_role_permissions
  title       = var.custom_role_id
  description = "Waverunner app custom role"
}

resource "google_service_account" "waverunner" {
  account_id = var.application_sa_name
  project    = var.project_id
}

resource "google_project_iam_member" "app_sa_custom_role" {
  project = var.project_id
  role    = google_project_iam_custom_role.waverunner.name
  member  = "serviceAccount:${google_service_account.waverunner.email}"
}

resource "google_project_iam_member" "app_sa_predefined_roles" {
  for_each = var.application_sa_roles
  project  = var.project_id
  role     = each.key
  member   = "serviceAccount:${google_service_account.waverunner.email}"
}


//--------------------------------------------------
//
//
//  Terraform code to create pubsub subscriptor push
//
//
//--------------------------------------------------

resource "google_pubsub_subscription" "migsc-push-subs" {
  name                       = var.pub_subs_name // "bms-subs-dev-mvp"
  project                    = var.project_id
  topic                      = google_pubsub_topic.topic.0.name
  labels                     = var.gcp_labels
  message_retention_duration = var.subs_message_retention_duration // "604800s"
  retain_acked_messages      = var.subs_retain_acked_messages      // false
  ack_deadline_seconds       = var.subs_ack_deadline_seconds       // 10
  expiration_policy {
    ttl = ""
  }
  retry_policy {
    minimum_backoff = var.subs_retry_policy["minimum_backoff"]
    maximum_backoff = var.subs_retry_policy["maximum_backoff"]
  }
  enable_message_ordering = var.subs_enable_message_ordering

  push_config {
    // push_endpoint = "https://${var.site_domain_name}/webhooks/status"
    push_endpoint = "https://${var.project_id}./webhooks/status"
    oidc_token {
      service_account_email = "${google_service_account.waverunner.email}"
      audience              = "${google_iap_client.project_client.client_id}"
    }

    attributes = {
      x-goog-version = var.x-goog-version // "v1"
    }
  }
}
