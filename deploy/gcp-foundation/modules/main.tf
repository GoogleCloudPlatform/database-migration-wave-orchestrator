/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#----------------------------------------------------------------------------------
#
# Configure GCP Consent Screen (Oauth2) and Client ID
#
#----------------------------------------------------------------------------------

data "google_project" "project" {
  project_id = var.project_id
  depends_on = [google_iap_brand.project_brand_nonex]
}

data "external" "migsc_iap_brand" {
  program = ["bash", "${path.module}/get-iap-brand.bash"]

  query = {
    project_id = var.project_id
  }
}

resource "google_iap_brand" "project_brand_nonex" {
  count             = data.external.migsc_iap_brand.result.brand == "" ? 1 : 0
  support_email     = var.oauth_support_contact_email
  application_title = "${var.deployment_name} Application"
  project           = var.project_id
  depends_on        = [google_project_service.gcp_services]
}

resource "google_iap_client" "project_client" {
  provider     = google
  display_name = "${var.deployment_name} Application Client"
  brand =  "projects/${data.google_project.project.number}/brands/${data.google_project.project.number}"
  depends_on = [google_project_service.gcp_services,google_iap_brand.project_brand_nonex]
}

resource "time_sleep" "wait_3_minutes" {
  create_duration = "180s"
}


#----------------------------------------------------------------------------------
#
# Create the VPC, subnets and Cloud DNS zone in which GCP resources will be created
#
#----------------------------------------------------------------------------------

# Create Network
resource "google_compute_network" "migsc-vpc" {
    count                   = var.create_vpc ? 1 : 0
    name                    = "${var.vpc_name}"
    auto_create_subnetworks = "false"
    project                 = var.project_id
    depends_on              = [google_project_service.gcp_services]
}

# Create Subnetwork with VPC flow enabled
resource "google_compute_subnetwork" "migsc-vpc-subnet-vpcnotflow" {
    count           = var.create_vpc && !var.vpc_flow ? 1 : 0
    name            = "${var.vpc_name}-subnet"
    ip_cidr_range   = var.subnet_cidr
    network         = "${var.vpc_name}"
    depends_on      = [google_compute_network.migsc-vpc,google_project_service.gcp_services]
    region          = var.migsc_region
    project         = var.project_id
}

# Create Subnetwork with VPC flow disabled
resource "google_compute_subnetwork" "migsc-vpc-subnet-vpcflow" {
    count           = var.create_vpc && var.vpc_flow ? 1 : 0
    name            = "${var.vpc_name}-subnet"
    ip_cidr_range   = var.subnet_cidr
    network         = "${var.vpc_name}"
    depends_on      = [google_compute_network.migsc-vpc,google_project_service.gcp_services]
    region          = var.migsc_region
    project         = var.project_id
    log_config {
      aggregation_interval = "INTERVAL_5_MIN"
      flow_sampling        = 0.5
      metadata             = "INCLUDE_ALL_METADATA"
    }
}

# Create VPC Firewall configuration
resource "google_compute_firewall" "migsc-allow-ssh" {
    count   = var.create_vpc ? 1 : 0
    name    = "${var.vpc_name}-allow-ssh"
    network = google_compute_network.migsc-vpc[count.index].name

    allow {
        protocol =  "tcp"
        ports    =  ["22"]
    }
    source_ranges = var.source_ranges_fw
    project       = var.project_id
    depends_on    = [google_project_service.gcp_services, google_compute_network.migsc-vpc]
}



#------------------------------------------------------------------------------------
#
# Pubsub Topic and related IAM permission
#
#------------------------------------------------------------------------------------

locals {
  default_ack_deadline_seconds = 10
  pubsub_svc_account_email     = "service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  gcp_labels = { for key, value in var.gcp_labels : lower(key) => lower(value) }
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
  project = var.project_id
  topic   = lookup(each.value, "dead_letter_topic", "projects/${var.project_id}/topics/${var.pubsub_topic}")
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${local.pubsub_svc_account_email}"
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
  project = var.project_id
  secret_id = "migsc-db-user-pass"
  replication {
    automatic = true
  }
  depends_on = [random_password.db_user_pass,google_project_service.gcp_services]
}

# add secret data for password secret
resource "google_secret_manager_secret_version" "db_user_pass" {
  secret = google_secret_manager_secret.db_user_pass.id
  secret_data = random_password.db_user_pass.result
  depends_on = [google_project_service.gcp_services]
}

# create a secret for connection string
resource "google_secret_manager_secret" "db_conn_string" {
  project = var.project_id
  secret_id = "migscaler-db-conn-string"
  replication {
    automatic = true
  }
  depends_on = [google_secret_manager_secret_version.db_user_pass, google_project_service.gcp_services]
}

# add secret data for connection string secret
resource "google_secret_manager_secret_version" "db_conn_string" {
  secret = google_secret_manager_secret.db_conn_string.id
  secret_data = "postgresql+psycopg2://${var.user_name}:${random_password.db_user_pass.result}@/${var.db_name}?host=/cloudsql/${var.project_id}:${var.migsc_region}:${var.db_instance_name}-${random_string.random.result}"
  depends_on = [random_string.random, google_project_service.gcp_services]
}

module "sql-db" {
  source  = "GoogleCloudPlatform/sql-db/google//modules/postgresql"
  version = "8.0.0"
  name             = "${var.db_instance_name}-${random_string.random.result}"
  user_labels      = var.gcp_labels
  db_name          = var.db_name
  user_name        = var.user_name
  user_password    = random_password.db_user_pass.result
  database_version = var.database_version
  project_id       = var.project_id
  zone             = var.zone
  region           = var.migsc_region
  tier             = var.tier
  maintenance_window_update_track = var.maintenance_window_update_track
  disk_size        = var.disk_size
  maintenance_window_hour = var.maintenance_window_hour
  ip_configuration = {
      # authorized_networks                = [{name = "network1", value = "0.0.0.0/0"},]
      authorized_networks                  = []
      ipv4_enabled                         = true
      private_network                      = ""
      require_ssl                          = null
  }
  backup_configuration = {
      enabled                              = var.enable_automatic_backup
      start_time                           = var.enable_automatic_backup ? var.backup_config.start_time : null
      location                             = var.enable_automatic_backup ? var.backup_config.location : null
      point_in_time_recovery_enabled       = var.enable_automatic_backup ? var.backup_config.point_in_time_recovery_enabled : false
      transaction_log_retention_days       = var.enable_automatic_backup ? var.backup_config.transaction_log_retention_days : null
      retained_backups                     = var.enable_automatic_backup ? var.backup_config.retained_backups : null
      retention_unit                       = var.enable_automatic_backup ? var.backup_config.retention_unit : null
  }
  activation_policy      = var.activation_policy
  availability_type      = var.availability_type
  db_charset             = var.db_charset
  db_collation           = var.db_collation
  random_instance_name   = var.random_instance_name
  create_timeout         = var.create_timeout
  delete_timeout         = var.delete_timeout
  update_timeout         = var.update_timeout
  enable_default_user    = var.enable_default_user
  enable_default_db      = var.enable_default_db
  disk_type              = var.disk_type
  deletion_protection    = var.deletion_protection
  depends_on             = [random_string.random]
}


#---------------------------------
#
# Terraform resource to create GCS 
#
#---------------------------------

resource "random_string" "random" {
  length  = 5
  special = false
  upper = false
}

resource "google_storage_bucket" "bucket" {
  name                        = "${var.migsc_bucket_name}-${random_string.random.result}"
  project                     = var.project_id
  location                    = var.migsc_region
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
  name          = "gce_metadata/"
  content       = "GCE Metadata"
  bucket        = "${google_storage_bucket.bucket.name}"
}


#-----------------------------------------
#
# Terraform module to enable projects APIs
#
#-----------------------------------------

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project = var.project_id
  service = each.key

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
  name = "${var.cloud_tasks_queue_name}-${random_string.random.result}"
  location = var.migsc_region
  project = var.project_id
  retry_config {
    max_attempts = 1
  }
}

# Create the Cloud Run service
resource "google_cloud_run_service" "run_service" {
  provider = google-beta
  name     = "${var.migsc_cloudrun_appl_name}-${random_string.random.result}" //
  location = var.migsc_region // var.bms_cloudrun_location  // "europe-west1"
  project  = var.project_id
  metadata {
     annotations = {
       "run.googleapis.com/ingress" =  "internal-and-cloud-load-balancing"
     }
     labels = var.gcp_labels
  }

  template {
    metadata {
        annotations = {
          "run.googleapis.com/cloudsql-instances" =  "${var.project_id}:${var.migsc_region}:${var.db_instance_name}-${random_string.random.result}"
          "autoscaling.knative.dev/maxScale"      = "10"
      }
    }
    spec {
      container_concurrency = var.bms_container_concurrency
      timeout_seconds       = var.bms_timeout_seconds
      service_account_name  = "${google_service_account.service_account_migscaler.email}"

      containers {
        image = var.migsc_cloudrun_image // "gcr.io/google-samples/hello-app:1.0"

      env {
        name  = "DATABASE_URL"
        value_from {
          secret_key_ref {
            name = google_secret_manager_secret.db_conn_string.secret_id
            key = "latest"
          }
        }
      }
      env {
        name  = "GCS_BUCKET"
        value = "${google_storage_bucket.bucket.name}"
      }
      env {
        name  = "GCS_ORACLE_BINARY_PREFIX"
        value = ""
      }
      env {
        name  = "GCS_DEPLOYMENT_CONFIG_PREFIX"
        value = "ansible_config-test"
      }
      env {
        name  = "USE_GCLOUD_LOGGING"
        value = "TRUE"
      }
      env {
        name  = "GCS_PUBSUB_TOPIC"
        value = "projects/${var.project_id}/topics/${google_pubsub_topic.topic.0.name}"
      }
      env {
        name  = "GCP_PUBSUB_TOPIC"
        value = "projects/${var.project_id}/topics/${google_pubsub_topic.topic.0.name}"
      }
      env {
        name  = "GCP_PROJECT_NAME"
        value = var.project_id
      }
      env {
        name  = "GCP_SERVICE_ACCOUNT"
        value = "${google_service_account.service_account_migscaler.email}"
      }
      env {
        name  = "GCP_PROJECT_NUMBER"
        value = "${data.google_project.project.number}"
      }
      env {
        name  = "GCP_CLOUD_TASKS_QUEUE"
        value = "projects/${var.project_id}/locations/${var.migsc_region}/queues/${google_cloud_tasks_queue.migsc-ctq.name}"
      }
      env {
        name  = "GCP_CLOUD_RUN_SERVICE_NAME"
        value = "projects/${var.project_id}/locations/${var.migsc_region}/services/${var.migsc_cloudrun_appl_name}-${random_string.random.result}"
      }
      env {
        name  = "GCP_OAUTH_CLIENT_ID"
        value = "${google_iap_client.project_client.client_id}"
      }
      env {
        name  = "GCP_LB_URL"
        value = "https://${var.site_domain_name}"
      }
    }
  }
  }
  traffic {
    percent         = var.bms_cloudrun_percent
    latest_revision = var.bms_cloudrun_revision
  }
  autogenerate_revision_name = true
  depends_on        = [google_pubsub_topic.topic, google_secret_manager_secret_version.db_conn_string, google_project_iam_member.iam-member-role1, google_project_iam_member.iam-member-role2, null_resource.grant_cloudrun_agent, google_iap_client.project_client, google_service_account.service_account_migscaler,google_cloud_tasks_queue.migsc-ctq]
}

resource "null_resource" "grant_cloudrun_agent" {
  provisioner "local-exec" {
    command = "gsutil iam ch serviceAccount:service-${data.google_project.project.number}@containerregistry.iam.gserviceaccount.com:objectViewer gs://artifacts.epam-bms-dev.appspot.com"
  }
  depends_on = [google_project_service.gcp_services]
}

# grant access to secret manager for cloud run
resource "google_secret_manager_secret_iam_member" "secret-access" {
  secret_id = google_secret_manager_secret.db_conn_string.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  depends_on = [google_secret_manager_secret.db_conn_string, google_cloud_run_service.run_service]
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
  retain_acked_messages      = var.subs_retain_acked_messages // false
  ack_deadline_seconds       = var.subs_ack_deadline_seconds // 10
  expiration_policy {
      ttl = ""
  }
  retry_policy {
      minimum_backoff = var.subs_retry_policy["minimum_backoff"]
      maximum_backoff = var.subs_retry_policy["maximum_backoff"]
  }
  enable_message_ordering    = var.subs_enable_message_ordering

  push_config {
    // push_endpoint = "https://${var.site_domain_name}/webhooks/status"
    push_endpoint = "${google_cloud_run_service.run_service.status[0].url}/webhooks/status"

    attributes = {
      x-goog-version = var.x-goog-version // "v1"
    }
  }
  depends_on = [google_cloud_run_service.run_service]
}

data "google_sql_database_instance" "dbinst" {
  name    =  var.db_instance_name
  project  = var.project_id
  depends_on = [module.sql-db]
}




//--------------------------------------------------
//
//
//  Cloud Identity Proxy
//
//
//--------------------------------------------------

resource "google_compute_region_network_endpoint_group" "cloudrun_neg" {
  provider = google-beta
  name                  = "${var.deployment_name}-lb-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.migsc_region
  project               = var.project_id
  cloud_run {
    service = google_cloud_run_service.run_service.name
  }
  depends_on = [google_cloud_run_service.run_service, time_sleep.wait_3_minutes]
}

# Get site name from provided cert name
data "external" "migsc_site_domain" {
  count   = var.use_ssl_certificates ? 1 : 0
  program = ["bash", "${path.module}/get-site-name.bash"]

  query = {
    project_id = var.project_id
    cert_name  = var.ssl_cert_name
  }
}

module "lb_http" {
  source  = "GoogleCloudPlatform/lb-http/google//modules/serverless_negs"
  version = "~> 4.1"

  project = var.project_id
  name    = "${var.deployment_name}-lb-https"

  create_address                  = var.create_address
  address                         = var.create_address ? null : var.lb_ext_ip
  ssl                             = var.ssl
  use_ssl_certificates            = var.use_ssl_certificates
  managed_ssl_certificate_domains = var.use_ssl_certificates ? [] : ["${var.site_domain_name}."]
  ssl_certificates                = var.use_ssl_certificates ? ["https://www.googleapis.com/compute/v1/projects/${var.project_id}/global/sslCertificates/${var.ssl_cert_name}"] : []
  https_redirect                  = true
  ssl_policy                      = "${google_compute_ssl_policy.min_tsl_version.self_link}"

  backends = {
    default = {
      description             = null
      enable_cdn              = false
      custom_request_headers  = null
      custom_response_headers = null
      security_policy         = null

      log_config = {
        enable      = true
        sample_rate = 1.0
      }

      groups = [
        {
          group = google_compute_region_network_endpoint_group.cloudrun_neg.id
        }
      ]

      iap_config = {
        enable               = true
        oauth2_client_id     = google_iap_client.project_client.client_id
        oauth2_client_secret = google_iap_client.project_client.secret
      }
    }
  }
  depends_on = [google_compute_region_network_endpoint_group.cloudrun_neg, google_iap_client.project_client, google_iap_brand.project_brand_nonex, google_project_service.gcp_services, google_pubsub_subscription.migsc-push-subs, google_compute_ssl_policy.min_tsl_version]
}

resource "google_compute_ssl_policy" "min_tsl_version" {
   name            =  "bms-min-tls-version"
   profile         =  "RESTRICTED"
   min_tls_version = "TLS_1_2"
}

data "google_dns_managed_zone" "dns_zone" {
  name = var.dns_zone_name
  depends_on = [google_project_service.gcp_services]
}

resource "google_dns_record_set" "frontend" {
  name = var.use_ssl_certificates ? "${data.external.migsc_site_domain[0].result.site}." : "${var.site_domain_name}."
  type = "A"
  ttl  = 300
  project = var.dns_project_name
  managed_zone = var.dns_zone_name

  rrdatas = [module.lb_http.external_ip]
  depends_on = [google_pubsub_subscription.migsc-push-subs]
}

resource "google_cloud_run_service_iam_member" "migsc-cloudrun-iam-member" {
  service = google_cloud_run_service.run_service.name
  location = google_cloud_run_service.run_service.location
  project = google_cloud_run_service.run_service.project
  role = "roles/run.invoker"
  member = "allUsers" //example-domain.co.jp
  depends_on = [google_cloud_run_service.run_service]
}

resource "google_iap_web_backend_service_iam_member" "group_member" {
  provider = google
  for_each            = toset(var.access_users)
  project             = var.project_id
  web_backend_service = module.lb_http.backend_services.default.name
  role                = "roles/iap.httpsResourceAccessor"
  member              = each.key
  depends_on          = [module.lb_http, google_pubsub_subscription.migsc-push-subs]
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

resource "google_project_iam_custom_role" "migscaler-role-appl" {
  project     = var.project_id
  role_id     = "${var.iam_role_migscaler_appl}${random_string.random.result}"
  permissions = var.permissions1
  title       = var.iam_role_migscaler_appl
  description = var.description1
}

resource "google_service_account" "service_account_migscaler" {
  account_id = var.service-account-migscaler-appl
  project    = var.project_id
}

resource "google_project_iam_member" "iam-member-role1" {
  project = var.project_id
  role    = "projects/${var.project_id}/roles/${google_project_iam_custom_role.migscaler-role-appl.role_id}"
  member  = "serviceAccount:${google_service_account.service_account_migscaler.email}"
  depends_on = [google_service_account.service_account_migscaler]
}

resource "google_project_iam_member" "iam-member-role2" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.service_account_migscaler.email}"
  depends_on = [google_service_account.service_account_migscaler]
}

resource "google_project_iam_member" "iam-member-role3" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.service_account_migscaler.email}"
  depends_on = [google_service_account.service_account_migscaler]
}

resource "google_project_iam_member" "iam-member-role4" {
  project = var.project_id
  role    = "roles/cloudsql.instanceUser"
  member  = "serviceAccount:${google_service_account.service_account_migscaler.email}"
  depends_on = [google_service_account.service_account_migscaler]
}

resource "google_project_iam_member" "iam-member-role5" {
  project = var.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.service_account_migscaler.email}"
  depends_on = [google_service_account.service_account_migscaler]
}

resource "google_project_iam_member" "iam-member-role6" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.service_account_migscaler.email}"
  depends_on = [google_service_account.service_account_migscaler]
}

resource "google_project_iam_member" "iam-member-role7" {
  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "serviceAccount:${google_service_account.service_account_migscaler.email}"
  depends_on = [google_service_account.service_account_migscaler]
}

resource "google_project_iam_member" "iam-member-role8" {
  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  depends_on = [google_service_account.service_account_migscaler]
}

//
//
// OUTPUT values
//
//

output "bucket_name" {
  value = google_storage_bucket.bucket.name
  description = "Name of the bucket"
}

output "bucket_url" {
  value = google_storage_bucket.bucket.url
  description = "URL of the bucket"
}

output "cloudrun_id" {
  value = google_cloud_run_service.run_service.id
  description = "ID of the cloudrun service"
}

output "cloudrun_url" {
  value = google_cloud_run_service.run_service.status[0].url
  description = "URL of the cloudrun service"
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

output "public_network" {
  value = var.create_vpc ? google_compute_network.migsc-vpc[0].name : var.public-network
  description = "Name of the public network"
}

output "pubsub_topic" {
  value       = length(google_pubsub_topic.topic) > 0 ? google_pubsub_topic.topic.0.name : ""
  description = "The name of the Pub/Sub topic"
}
 
output "pubsub_subscriptor" {
  value = google_pubsub_subscription.migsc-push-subs.name
  description = "Pubsub subsciptor name"
}

output "sa_appl" {
  value = google_service_account.service_account_migscaler.account_id
  description = "Service Account for the migscaler appl"
}

output "iam_role_appl" {
  value = google_project_iam_custom_role.migscaler-role-appl.role_id
  description = "IAM Role for migscaler appl"
}

output "application_url" {
  value = "https://${var.site_domain_name}"
  description = "application URL"
}
