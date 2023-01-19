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

//
//
// VPC
//
//

variable "public-subnetwork" {
  type        = string
  description = "Name of the public subnetwork"
  default     = "migsc-subnet"
}

variable "public-network" {
  type        = string
  description = "Name of the VPC network"
  default     = "migsc-vpc-network"
}

variable "create_vpc" {
  type        = bool
  description = "Condition to create VCP"
  default     = true
}

variable "create_dns_zone" {
  type        = bool
  description = "Bool value to create new zone"
  default     = false
}

variable "bms-dns-name" {
  type        = string
  description = "DNS name"
  default     = "migsc-app.localdomain."
}

variable "subnet_cidr" { // VPC
  description = "CIDR block of the public subnet"
  default = "10.0.0.0/24"
}

variable "vpc_name" { // VPC
  description = "VPC Name"
  default = "migsc-vpc"
}

variable "bms-dns-zone-name" {
  type        = string
  description = "DNS zone name"
  default     = "migsc-dns-zone"
}

variable "project_id" {
  type        = string
  description = "Project where the GCE will be created"
  default     = "migsc-gcp-prj-v00"
}

variable "migsc_region" {
  type        = string
  description = "Region where migScaler resources will be created"
  default     = "europe-west1"
}

variable "source_ranges_fw" {
  type        = list
  description = "Ranges to be allowed in FW rules - Port 22"
  default     = ["195.56.119.0/24" ,"10.0.2.0/24"]
}



//
//
// Cloud SQL PostgreSQL
//
//

variable "zone" {
    type         = string
    default      = "europe-west1-b"
}

variable "db_instance_name" {
    type         = string
    default      = "migsc-db-instance"    // Instance name
}

variable "db_name" {
    type         = string
    default      = "migsc-db-name"
}

variable "user_name" {
    type         = string
    default      = "migsc-db-user"
}

variable "activation_policy" {
    type         = string
    default      = "ALWAYS"
}

variable "availability_type" {
    type         = string
    default      = "ZONAL"
}

variable "db_charset" {
    type         = string
    default      = "UTF8"
}

variable "db_collation" {
    type         = string
    default      = "en_US.UTF8"
}

variable "random_instance_name" {
    type         = bool
    default      = false
}

variable "create_timeout" {
    type         = string
    default      = "45m"
}

variable "additional_databases" {
    type = list(object({
        name          = string
        charset       = string
        collation     = string
    }))
    default           = []
}

variable "database_version" {
    type          = string
    default       = "POSTGRES_13"
}

variable "maintenance_window_day" {
    type         = number
    default      = 1
}

variable "delete_timeout" {
    type         = string
    default      = "45m"
}

variable "deletion_protection" {
    type         = bool
    default      = false
}

variable "disk_autoresize" {
    type         = bool
    default      = true
}

variable "disk_size" {
    default      = 10
}

variable "disk_type" {
    type         = string
    default      = "PD_SSD"
}

variable "ip_configuration" {
    type = object ({
        authorized_networks                = list(map(string))
        ipv4_enabled                       = bool
        private_network                    = string
        require_ssl                        = bool
    })
    default = {
      authorized_networks                  = [{name = "network1", value = "0.0.0.0/0"},]
      ipv4_enabled                         = true
      private_network                      = "projects/or2-msq-go3-inv-t1iylu/global/networks/network-demo-mvp-vpc"
      require_ssl                          = null
    }
}

variable "encryption_key_name" {
    type         = string
    default      = null
}

variable "backup_config" {
    type = object({
        enabled                            = bool
        start_time                         = string
        location                           = string
        point_in_time_recovery_enabled     = bool
        transaction_log_retention_days     = string
        retained_backups                   = number
        retention_unit                     = string
    })
    default = {
      enabled                              = true
      location                             = null
      point_in_time_recovery_enabled       = true
      retained_backups                     = 3
      retention_unit                       = "COUNT"
      start_time                           = null
      transaction_log_retention_days       = 4
    }
}

variable "enable_automatic_backup" {
    type         = bool
    default      = true
}

variable "database_flags" {
    type         = list(object({
        name     = string
        value    = string
    }))
    default      = []
}

variable "insights_config" {
    type = object ({
        query_string_length                = number
        record_application_tags            = bool
        record_client_address              = bool
    })
    default                                = null
}

variable "maintenance_window_hour" {
    type         = number
    default      = "23"
}

variable "iam_user_emails" {
    type         = list(string)
    default      = []
}

variable "pricing_plan" {
    type         = string
    default      = "PER_USE"
}

variable "query_insights_enabled" {
    type         = bool
    default      = true
}

variable "tier" {
    type         = string
    default      = "db-custom-2-3840"
}

variable "maintenance_window_update_track" {
    type         = string
    default      = "canary"
}

variable "update_timeout" {
    type         = string
    default      = "45m"
}

variable "user_labels" {
    type         = map(string)
    default      = {}
}

variable "additional_users" {
    type = list(object({
        name            = string
        password        = string
    }))
    default             = []
}

variable "module_depends_on" {
    type        = list(any)
    default     = [  ]
}

variable "enable_default_db" {
    type         = bool
    default      = true
}

variable "impersonate_sa" {
    type         = bool
    default      = false
}

variable "sa_tf_impersonate" {
    type         = string
    default      = null
}

variable "enable_default_user" {
    type         = bool
    default      = true
}


//
//
// Template for GCE
//
//

// Required values (most of them already have default values)

variable "create_topic" {
  type        = bool
  description = "Specify true if you want to create a topic"
  default     = true
}

variable "pubsub_labels" {
  type = map
  default = {
    env       = "dev"
    release   = "mvp"
  }
}

variable "pubsub_topic" {
  type        = string
  description = "The Pub/Sub topic name"
  default     = "migsc-ps-topic"
}

variable "topic_kms_key_name" {
  type        = string
  description = "The resource name of the Cloud KMS CryptoKey to be used to protect access to messages published on this topic."
  default     = null
}

variable "message_storage_policy" {
  type        = map(any)
  description = "A map of storage policies. Default - inherit from organization's Resource Location Restriction policy."
  default     = {}
}

variable "push_subscriptions" {
  type        = list(map(string))
  description = "The list of the push subscriptions"
  default     = []
}

variable "topic_labels" {
  type        = map(string)
  description = "A map of labels to assign to the Pub/Sub topic"
  default     = {}
}


//
// Cloudrun and Pubsub
//

variable "pub_subs_name" {
  type        = string
  description = "BMS pubsub subscriptor - push"
  default     = "migsc-ps-subscriptor"
}

variable "subs_message_retention_duration" {
  type        = string
  description = "Pub Sub message retention duration"
  default     = "28800s"
}

variable "subs_retain_acked_messages" {
  type        = bool
  description = "Subs retain acked messages"
  default     = false
}

variable "migsc_cloudrun_appl_name" {
  type        = string
  description = "Cloud appl name"
  default     = "migsc-cr-app"
}

variable "bms_cloudrun_location" {
  type        = string
  description = "Cloud appl location"
  default     = "europe-west1"
}

variable "bms_container_concurrency" {
  type        = number
  description = "Cloud Run Container concurrency"
  default = 80
}

variable "bms_timeout_seconds" {
  type        = number
  description = "Cloud Run timeout"
  default = 300
}

variable "migsc_cloudrun_image" {
  type        = string
  description = "GCP cloudrun image"
  default     = "gcr.io/epam-bms-dev/bms-app/bms-app:latest"
}

variable "bms_cloudrun_revision" {
  type        = bool
  description = "Cloud Run use latest revision"
  default     = true
}

variable "bms_cloudrun_percent" {
  type        = number
  description = "Cloud Run percent of the traffic"
  default     = 100
}

variable "subs_ack_deadline_seconds" {
  type        = number
  description = "Subs ack deadline seconds"
  default     = 10
}

variable "subs_retry_policy" {
  type = map
  default = {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

variable "subs_enable_message_ordering" {
  type        = bool
  description = "Subs enable message ordering"
  default     = true
}

variable "x-goog-version" {
  type        = string
  description = "x-goog-version for Push subscriptors"
  default     = "v1"
}


//
// GCS
//

variable "migsc_bucket_name" {
    type         = string
    default      = "migsc-gcs"
}

variable "location" {
    type         = string
    default      = "europe-west1"
}

variable "encryption" {
  description = "A Cloud KMS key that will be used to encrypt objects inserted into this bucket"
  type = object({
    default_kms_key_name = string
  })
  default = null
}

variable "versioning" {
  description = "While set to true, versioning is fully enabled for this bucket."
  type        = bool
  default     = true
}

variable "force_destroy" {
  description = "When deleting a bucket, this boolean option will delete all contained objects. If false, Terraform will fail to delete buckets which contain objects."
  type        = bool
  default     = true
}

variable "lifecycle_rules" {
  description = "The bucket's Lifecycle Rules configuration."
  type = list(object({
    action = any
    condition = any
  }))
  default = []
}

variable "log_bucket" {
  description = "The bucket that will receive log objects."
  type        = string
  default     = null
}

variable "retention_policy" {
  description = "Configuration of the bucket's data retention policy for how long objects in the bucket should be retained."
  type = object({
    is_locked        = bool
    retention_period = number
  })
  default = null
}

variable "iam_members" {
  description = "The list of IAM members to grant permissions on the bucket."
  type = list(object({
    role   = string
    member = string
  }))
  default = []
}

variable "labels" {
  description = "A set of key/value label pairs to assign to the bucket."
  type        = map(string)
  default     = {
     "application" = "bms",
     "environment" = "dev"
  }
}

variable "log_object_prefix" {
  description = "The object prefix for log objects. If it's not provided, by default GCS sets this to this bucket's name"
  type        = string
  default     = null
}

variable "storage_class" {
  description = "The Storage Class of the new bucket."
  type        = string
  default     = "STANDARD"
}

variable "bucket_policy_only" {
  description = "Enables Bucket Policy Only access to a bucket."
  type        = bool
  default     = true
}

//
//
// APIs
//
//

variable "gcp_service_list" {
  description ="The list of apis necessary for the project"
  type = list(string)
  default = [
    "compute.googleapis.com",
    "run.googleapis.com",
    "vpcaccess.googleapis.com",
    "sqladmin.googleapis.com",
    "dns.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudfunctions.googleapis.com",
    "oslogin.googleapis.com",
    "pubsub.googleapis.com",
    "stackdriver.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com",
    "sql-component.googleapis.com",
    "servicenetworking.googleapis.com",
    "iap.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "baremetalsolution.googleapis.com",
    "sourcerepo.googleapis.com",
    "identitytoolkit.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "domains.googleapis.com",
    "cloudtasks.googleapis.com"
    // "vpcaccess.googleapis.com"
  ]
}



//
//
// Service accounts and roles
//
//

variable "service-account-migscaler-appl" {
  type        = string
  description = "Service Account for Application"
  default     = "migsc-app-iam-sa"
}

variable "description1" {
  type        = string
  description = "Custom role - bms_toolkit_appl_dev"
  default     = ""
}

variable "iam_role_migscaler_appl" {
  type        = string
  description = "ID of the Custom Role."
  default     = "migsc_app_iam_role"
}


//
//
//
// Cloud Identity Proxy
//
//
//

variable "deployment_name" {
  default = "migscaler"
}

variable "deployment_name_short" {
  default = "migsc"
}

variable "access_users" {
  description = "Access Users"
  default = ["allAuthenticatedUsers"]
  // default = ["user:jose_enrique_hernandez@epam.com"]
}

variable "oauth_support_contact_email" {
  description = "email address to list on oauth consent screen"
  default = "migScaler-support@gmail.com"
}

variable "create_address" {
  type        = bool
  description = "Create new external IP for LB"
  default     = false
}

variable "ssl" {
  type        = bool
  description = "Use SSL cert or not"
  default     = true
}

variable "use_ssl_certificates" {
  type        = bool
  description = "Use an existing SSL cert or not"
  default     = false
}

variable "ssl_certificates" {
  type        = list
  description = "SSL cert to use (if use_ssl_certificates is true)"
  default     = null
}

variable "lb_ext_ip" {
  description = "Existing external IP address for Load Balancer"
  default = "127.0.0.1"
}

variable "ssl_cert_name" {
  type        = string
  description = "SSL Certificate name for Load Balancer"
}

variable "dns_project_name" {
  description = "Project with dns zone"
  default = "great-migrator-dns"
}

variable "dns_zone_name" {
  description = "Managed zone name"
  default = "greatmigrator-root"
}

variable "site_domain_name" {
  description = "Domain name for APP"
  default = "test-migscaler.greatmigrator.joonix.net."
}

variable "brand_file" {
  description = "Brand File"
  default = "brand_id"
}

variable "gcp_labels" {
  type = map
  default = {} 
}

variable "vpc_flow" {
  type = bool
  default = true
}

variable "cloud_tasks_queue_name" {
  description = "CloutTasks queue name"
  default = "migsc-queue"
}


variable "permissions1" {
  type        = list(string)
  description = "IAM permissions assigned to Custom Role."
  default     = [
    "compute.diskTypes.get", 
    "compute.diskTypes.list", 
    "compute.disks.addResourcePolicies", 
    "compute.disks.create", 
    "compute.disks.createSnapshot", 
    "compute.disks.delete", 
    "compute.disks.get", 
    "compute.disks.list", 
    "compute.disks.removeResourcePolicies", 
    "compute.disks.resize", 
    "compute.disks.setIamPolicy", 
    "compute.disks.setLabels", 
    "compute.disks.update", 
    "compute.disks.use", 
    "compute.disks.useReadOnly", 
    "compute.images.create", 
    "compute.images.delete", 
    "compute.images.deprecate", 
    "compute.images.get", 
    "compute.images.getFromFamily", 
    "compute.images.getIamPolicy", 
    "compute.images.list", 
    "compute.images.setIamPolicy", 
    "compute.images.update", 
    "compute.images.useReadOnly", 
    "compute.instanceGroups.get", 
    "compute.instanceGroups.list", 
    "compute.instances.attachDisk", 
    "compute.instances.create", 
    "compute.instances.delete", 
    "compute.instances.detachDisk", 
    "compute.instances.get", 
    "compute.instances.getGuestAttributes", 
    "compute.instances.getShieldedVmIdentity", 
    "compute.instances.list", 
    "compute.instances.listReferrers", 
    "compute.instances.osAdminLogin", 
    "compute.instances.osLogin", 
    "compute.instances.removeMaintenancePolicies", 
    "compute.instances.removeResourcePolicies", 
    "compute.instances.reset", 
    "compute.instances.resume", 
    "compute.instances.sendDiagnosticInterrupt", 
    "compute.instances.setDeletionProtection", 
    "compute.instances.setDiskAutoDelete", 
    "compute.instances.setIamPolicy", 
    "compute.instances.setLabels", 
    "compute.instances.setMachineResources", 
    "compute.instances.setMachineType", 
    "compute.instances.setMetadata", 
    "compute.instances.setMinCpuPlatform", 
    "compute.instances.setScheduling", 
    "compute.instances.setServiceAccount", 
    "compute.instances.setShieldedInstanceIntegrityPolicy", 
    "compute.instances.setShieldedVmIntegrityPolicy", 
    "compute.instances.setTags", 
    "compute.instances.start", 
    "compute.instances.startWithEncryptionKey", 
    "compute.instances.stop", 
    "compute.instances.suspend", 
    "compute.instances.update", 
    "compute.instances.updateAccessConfig", 
    "compute.instances.updateDisplayDevice", 
    "compute.instances.updateNetworkInterface", 
    "compute.instances.updateSecurity", 
    "compute.instances.updateShieldedInstanceConfig", 
    "compute.instances.updateShieldedVmConfig", 
    "compute.instances.use", 
    "compute.instances.useReadOnly", 
    "compute.machineTypes.get", 
    "compute.machineTypes.list", 
    "compute.networkEndpointGroups.get", 
    "compute.networkEndpointGroups.list", 
    "compute.networkEndpointGroups.use", 
    "compute.networks.access", 
    #"compute.networks.create", 
    #"compute.networks.delete", 
    "compute.networks.get", 
    "compute.networks.getEffectiveFirewalls", 
    "compute.networks.list", 
    "compute.networks.mirror", 
    "compute.networks.update", 
    "compute.networks.use", 
    "compute.networks.useExternalIp", 
    "compute.projects.get", 
    "compute.regionOperations.get", 
    "compute.regionOperations.list", 
    "compute.regionUrlMaps.get", 
    "compute.regionUrlMaps.list", 
    "compute.regions.get", 
    "compute.regions.list", 
    "compute.routers.create", 
    "compute.routers.delete", 
    "compute.routers.get", 
    "compute.routers.list", 
    "compute.routers.update", 
    "compute.routers.use", 
    "compute.routes.create", 
    "compute.routes.delete", 
    "compute.routes.get", 
    "compute.routes.list", 
    "compute.subnetworks.create", 
    "compute.subnetworks.delete", 
    "compute.subnetworks.expandIpCidrRange", 
    "compute.subnetworks.get", 
    "compute.subnetworks.getIamPolicy", 
    "compute.subnetworks.list", 
    "compute.subnetworks.mirror", 
    "compute.subnetworks.setIamPolicy", 
    "compute.subnetworks.setPrivateIpGoogleAccess", 
    "compute.subnetworks.update", 
    "compute.subnetworks.use", 
    "compute.subnetworks.useExternalIp", 
    "compute.zoneOperations.get", 
    "compute.zoneOperations.list", 
    "compute.zones.get", 
    "compute.zones.list", 
    "firebase.projects.get", 
    "iam.serviceAccountKeys.get", 
    "iam.serviceAccountKeys.list", 
    "iam.serviceAccounts.actAs", 
    "iam.serviceAccounts.create", 
    "iam.serviceAccounts.delete", 
    "iam.serviceAccounts.disable", 
    "iam.serviceAccounts.enable", 
    "iam.serviceAccounts.get", 
    "iam.serviceAccounts.getAccessToken", 
    "iam.serviceAccounts.getIamPolicy", 
    "iam.serviceAccounts.list", 
    "iam.serviceAccounts.setIamPolicy", 
    "iam.serviceAccounts.update", 
    "logging.buckets.get", 
    "logging.buckets.list", 
    "logging.cmekSettings.get", 
    "logging.exclusions.get", 
    "logging.exclusions.list", 
    "logging.fields.access", 
    "logging.locations.list", 
    "logging.logEntries.create", 
    "logging.logEntries.list", 
    "logging.logMetrics.get", 
    "logging.logMetrics.list", 
    "logging.logServiceIndexes.list", 
    "logging.logServices.list", 
    "logging.logs.list", 
    "logging.notificationRules.get", 
    "logging.notificationRules.list", 
    "logging.operations.get", 
    "logging.operations.list", 
    "logging.queries.get", 
    "logging.queries.list", 
    "logging.queries.listShared", 
    "logging.queries.share", 
    "logging.queries.update", 
    "logging.sinks.create", 
    "logging.sinks.get", 
    "logging.sinks.list", 
    "logging.usage.get", 
    "logging.views.access", 
    "logging.views.create", 
    "logging.views.get", 
    "logging.views.list", 
    "logging.views.listLogs", 
    "logging.views.listResourceKeys", 
    "logging.views.listResourceValues", 
    "logging.views.update", 
    "monitoring.groups.create", 
    "monitoring.groups.delete", 
    "monitoring.groups.get", 
    "monitoring.groups.list", 
    "monitoring.notificationChannels.create", 
    "monitoring.notificationChannels.delete", 
    "monitoring.notificationChannels.get", 
    "monitoring.notificationChannels.list", 
    "monitoring.services.create", 
    "monitoring.services.delete", 
    "monitoring.services.get", 
    "monitoring.services.list", 
    "monitoring.services.update", 
    "monitoring.timeSeries.create", 
    "monitoring.timeSeries.list", 
    "pubsub.schemas.attach", 
    "pubsub.schemas.create", 
    "pubsub.schemas.delete", 
    "pubsub.schemas.get", 
    "pubsub.schemas.getIamPolicy", 
    "pubsub.schemas.list", 
    "pubsub.schemas.setIamPolicy", 
    "pubsub.schemas.validate", 
    "pubsub.snapshots.create", 
    "pubsub.snapshots.delete", 
    "pubsub.snapshots.get", 
    "pubsub.snapshots.getIamPolicy", 
    "pubsub.snapshots.list", 
    "pubsub.snapshots.seek", 
    "pubsub.snapshots.setIamPolicy", 
    "pubsub.snapshots.update", 
    "pubsub.subscriptions.consume", 
    "pubsub.subscriptions.create", 
    "pubsub.subscriptions.delete", 
    "pubsub.subscriptions.get", 
    "pubsub.subscriptions.getIamPolicy", 
    "pubsub.subscriptions.list", 
    "pubsub.subscriptions.setIamPolicy", 
    "pubsub.subscriptions.update", 
    "pubsub.topics.attachSubscription", 
    "pubsub.topics.create", 
    "pubsub.topics.delete", 
    "pubsub.topics.detachSubscription", 
    "pubsub.topics.get", 
    "pubsub.topics.getIamPolicy", 
    "pubsub.topics.list", 
    "pubsub.topics.publish", 
    "pubsub.topics.setIamPolicy", 
    "pubsub.topics.update", 
    "pubsub.topics.updateTag", 
    "resourcemanager.projects.get", 
    "run.services.get", 
    "run.services.update", 
    "secretmanager.locations.get", 
    "secretmanager.locations.list", 
    "secretmanager.secrets.create", 
    "secretmanager.secrets.delete", 
    "secretmanager.secrets.get", 
    "secretmanager.secrets.list", 
    "secretmanager.secrets.update", 
    "secretmanager.versions.access", 
    "secretmanager.versions.add", 
    "secretmanager.versions.destroy", 
    "secretmanager.versions.disable", 
    "secretmanager.versions.enable", 
    "secretmanager.versions.get", 
    "secretmanager.versions.list", 
    "servicenetworking.services.addSubnetwork", 
    "source.repos.get", 
    "source.repos.list", 
    "storage.buckets.create", 
    "storage.buckets.createTagBinding", 
    "storage.buckets.delete", 
    "storage.buckets.deleteTagBinding", 
    "storage.buckets.get", 
    "storage.buckets.getIamPolicy", 
    "storage.buckets.list", 
    "storage.buckets.listTagBindings", 
    "storage.buckets.setIamPolicy", 
    "storage.buckets.update", 
    "storage.multipartUploads.abort", 
    "storage.multipartUploads.create", 
    "storage.multipartUploads.list", 
    "storage.multipartUploads.listParts", 
    "storage.objects.create", 
    "storage.objects.delete", 
    "storage.objects.get", 
    "storage.objects.getIamPolicy", 
    "storage.objects.list", 
    "storage.objects.setIamPolicy", 
    "storage.objects.update", 
    "compute.zones.list", 
    "compute.zones.get", 
    "cloudsql.instances.get", 
    "cloudsql.instances.connect", 
    "cloudtasks.tasks.list", 
    "cloudtasks.tasks.get", 
    "cloudtasks.tasks.create", 
    "cloudtasks.tasks.delete", 
    "cloudtasks.tasks.run", 
    "cloudtasks.tasks.fullView", 
    "cloudtasks.locations.list", 
    "cloudtasks.locations.get", 
    "cloudtasks.queues.list", 
    "cloudtasks.queues.get", 
    "cloudtasks.queues.update", 
    "cloudtasks.queues.purge", 
    "cloudtasks.queues.pause", 
    "cloudtasks.queues.resume"
    ]
}
