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

module "gcp-foundation" {

  source                         = "./modules"

  #--------------------
  # REQUIRED Parameters
  #--------------------
  project_id                     = "_PROJECT_ID_"

  // ONLY IF create_vpc is false
  public-network                 = "migsc-network"
  public-subnetwork              = "migsc-subnetwork"

  // CLOUD LB
  ssl                            = true
  create_address                 = true
  use_ssl_certificates           = false
  lb_ext_ip                      = "EXISTING_IP_ADDRESS"
  ssl_cert_name                  = "migs-lb-cert"
  site_domain_name               = "test-migscaler.greatmigrator.joonix.net"

  dns_project_name               = "great-migrator-dns"
  dns_zone_name                  = "greatmigrator-root"

  // CLOUD RUN
  migsc_cloudrun_image           = "gcr.io/epam-bms-dev/bms-app/bms-app:latest"

  // CLOUD IAP
  oauth_support_contact_email    = "oauth_supportemail@gmail.com"

  #--------------------
  # OPTIONAL Parameters
  #--------------------
  migsc_region                   = "europe-west1"
  zone                           = "europe-west1-b"

  // GCS
  migsc_bucket_name              = "bms-gcs"

  // CLOUD RUN
  migsc_cloudrun_appl_name       = "migscaler-appl"

  // VPC
  create_vpc                     = true
  vpc_flow                       = false // NOTE: VPC flow logs generates charges. See: https://cloud.google.com/vpc/pricing

  // DB
  db_instance_name               = "migsc-db-instance"
  db_name                        = "migsc-db-name"
  user_name                      = "migsc-db-user"
  enable_automatic_backup        = true

  // SA AND ROLE
  service-account-migscaler-appl = "migsc-app-iam-sa"
  iam_role_migscaler_appl        = "migsc_app_iam_role"

  // SA FOR Terraform IMPERSONATION
  impersonate_sa                 = false
  sa_tf_impersonate              = "sa-test-migscaler"

  // PUBSUB
  pubsub_topic                   = "migsc-ps-topic"
  pub_subs_name                  = "migsc-ps-subscriptor"
  
  gcp_labels = {
    created_by  = "terraform"
    environment = "uat"
    app_name    = "migscaler"
    app_release = "mvp"
  }
}

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

output "cloudrun_id" {
  value       = module.gcp-foundation.cloudrun_id
  description = "ID of the cloudrun service"
}

output "cloudrun_url" {
  value       = module.gcp-foundation.cloudrun_url
  description = "URL of the cloudrun service"
}

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

output "public_network" {
  value       = module.gcp-foundation.public_network
  description = "Name of the public network"
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

output "application_url" {
  value       = module.gcp-foundation.application_url
  description = "Application URL"
}
