variable "project_id" {
  type        = string
  description = "Project where the application will be created"
}

variable "region" {
  type        = string
  description = "Region where Waverunner resources will be created"
  default     = "us-central1"
}

variable "app_engine_location" {
  type        = string
  description = "Location where Waverunner app will be created"
  default     = "us-central"
}

//
//
// Cloud SQL PostgreSQL
//
//

variable "zone" {
  type    = string
  default = "us-central1-a"
}

variable "db_instance_name" {
  type    = string
  default = "waverunner-db-instance" // Instance name
}

variable "db_name" {
  type    = string
  default = "waverunner-db-name"
}

variable "user_name" {
  type    = string
  default = "waverunner-db-user"
}

variable "activation_policy" {
  type    = string
  default = "ALWAYS"
}

variable "availability_type" {
  type    = string
  default = "ZONAL"
}

variable "db_charset" {
  type    = string
  default = "UTF8"
}

variable "db_collation" {
  type    = string
  default = "en_US.UTF8"
}

variable "random_instance_name" {
  type    = bool
  default = false
}

variable "create_timeout" {
  type    = string
  default = "45m"
}


variable "database_version" {
  type    = string
  default = "POSTGRES_13"
}

variable "delete_timeout" {
  type    = string
  default = "45m"
}

variable "deletion_protection" {
  type    = bool
  default = false
}

variable "disk_size" {
  default = 10
}

variable "disk_type" {
  type    = string
  default = "PD_SSD"
}

variable "backup_config" {
  type = object({
    enabled                        = bool
    start_time                     = string
    location                       = string
    point_in_time_recovery_enabled = bool
    transaction_log_retention_days = string
    retained_backups               = number
    retention_unit                 = string
  })
  default = {
    enabled                        = true
    location                       = null
    point_in_time_recovery_enabled = true
    retained_backups               = 3
    retention_unit                 = "COUNT"
    start_time                     = null
    transaction_log_retention_days = 4
  }
}

variable "enable_automatic_backup" {
  type    = bool
  default = true
}

variable "maintenance_window_hour" {
  type    = number
  default = "23"
}

variable "tier" {
  type    = string
  default = "db-custom-2-3840"
}

variable "maintenance_window_update_track" {
  type    = string
  default = "canary"
}

variable "update_timeout" {
  type    = string
  default = "45m"
}

variable "enable_default_db" {
  type    = bool
  default = true
}

variable "enable_default_user" {
  type    = bool
  default = true
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

variable "pubsub_topic" {
  type        = string
  description = "The Pub/Sub topic name"
  default     = "waverunner-ps-topic"
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

//
// Cloudrun and Pubsub
//

variable "pub_subs_name" {
  type        = string
  description = "BMS pubsub subscription - push"
  default     = "waverunner-ps-subscription"
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


variable "waverunner_image" {
  type        = string
  description = "GCP cloudrun image"
  default     = "gcr.io/epam-bms-dev/bms-app/bms-app:latest"
}

variable "subs_ack_deadline_seconds" {
  type        = number
  description = "Subs ack deadline seconds"
  default     = 10
}

variable "subs_retry_policy" {
  type = map(any)
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
  description = "x-goog-version for Push subscription"
  default     = "v1"
}


//
// GCS
//

variable "bucket_name" {
  type    = string
  default = "waverunner-gcs"
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
    action    = any
    condition = any
  }))
  default = []
}

variable "log_bucket" {
  description = "The bucket that will receive log objects."
  type        = string
  default     = null
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
  description = "The list of apis necessary for the project"
  type        = list(string)
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
    "cloudtasks.googleapis.com",
    "appengineflex.googleapis.com"
    // "vpcaccess.googleapis.com"
  ]
}



//
//
// Service accounts and roles
//
//

variable "application_sa_name" {
  type        = string
  description = "Service Account for Application"
  default     = "waverunner-sa"
}

variable "custom_role_id" {
  type        = string
  description = "ID of the Custom Role."
  default     = "waverunner_sa_custom_role"
}


//
//
//
// Cloud Identity Proxy
//
//
//

variable "deployment_name" {
  default = "waverunner"
}


variable "access_users" {
  type        = list(string)
  description = "Users that will be able to access the application. These values should be marked as \"user:jane@acme.com\" or \"group:app-group@acme.com\""
}

variable "oauth_support_contact_email" {
  description = "Email address to list on oauth consent screen"
}


variable "gcp_labels" {
  type    = map(any)
  default = {}
}

variable "cloud_tasks_queue_name" {
  description = "CloutTasks queue name"
  default     = "migsc-queue"
}


variable "application_sa_custom_role_permissions" {
  type        = list(string)
  description = "IAM permissions assigned to Custom Role."
  default = [
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
    "compute.networks.create",
    "compute.networks.delete",
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


variable "application_sa_roles" {
  type        = set(string)
  description = "Predefined roles that will be assigned to the waverunner service account"
  default = [
    "roles/secretmanager.secretAccessor",
    "roles/run.invoker",
    "roles/cloudsql.instanceUser",
    "roles/cloudtasks.enqueuer",
    "roles/pubsub.publisher",
    "roles/iap.httpsResourceAccessor",
    "roles/iap.httpsResourceAccessor",
    "roles/logging.logWriter"
  ]
}