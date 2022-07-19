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

// Required values (most of them already have default values)

variable "public-subnetwork" {
  type        = string
  description = "Name of the public subnetwork"
  default     = null
}

variable "vpc_name" { // VPC
  description = "VPC Name"
  default = "migsc-vpc"
}

variable "project_id" {
  type        = string
  description = "Project where the GCE will be created"
  // default     = "epam-bms-dev"
  default     = "or2-msq-go3-inv-t1iylu"
}

variable "gce_region" {
  type        = string
  description = "Region where the VM will be created"
  default     = "europe-west1"
}

variable "gce_zone" {
  type        = string
  description = "Zone where the VM will be created"
  default     = "europe-west1-b"
}

variable "public-network" {
  type        = string
  description = "Name of the VPC network"
  default     = "migsc-vpc"
}

variable "gce_source_image-rac" {
  type        = string
  description = "Source image for RAC"
  default     = "bms-rac-epam-dev"
  // default     = "migsc-gce-image-rac"
}

variable "gce_source_image-non-rac" {
  type        = string
  description = "Source image for non-RAC"
  default     = "rhel-cloud/rhel-7"
}

// Optional values

variable "bms_gce_addressing_type" {
  type        = string
  description = "IPv4 address name"
  default     = "migsc-ipv4-addr"
}

variable "gce_auto_delete" {
  type        = bool
  description = "Value for disks - Auto delete creation"
  default     = true
}

variable "gce_autom_restart" {
  type        = bool
  description = "GCE Automatic Restart"
  default     = true
}

variable "gce_disk_boot" {
  type        = string
  default     = null
}

variable "gce_can_ip_forward" {
  type        = bool
  description = "Enable IP forwarding, for NAT instances for example"
  default     = false
}

variable "gce_description" {
  type        = string
  description = "Description of the TF resource GCE"
  default     = null
}

variable "gce_disk_size" {
  type        = string
  description = "Disk size"
  default     = null
}

variable "gce_disk_type" {
  type        = string
  description = "Disk type"
  default     = null
}

variable "bms_gce_common_disks" {
  description = "List of maps of additional disks. See https://www.terraform.io/docs/providers/google/r/compute_instance_template.html#disk_name"
  type = list(object({
    /* disk_name    = string */
    /* device_name  = string */
    auto_delete  = bool
    boot         = bool
    disk_size_gb = number
    disk_type    = string
  }))
  default = [
  {
    /* disk_name    = "tf-bms-disk-dev-u01-" */
    /* device_name  = "tf-bms-disk-dev-u01-" */
    auto_delete  = true
    boot         = false
    disk_size_gb = "50"
    disk_type    = "pd-ssd"
  },
  {
    /* disk_name    = "tf-bms-disk-dev-u02-" */
    /* device_name  = "tf-bms-disk-dev-u02-" */
    auto_delete  = true
    boot         = false
    disk_size_gb = "10"
    disk_type    = "pd-balanced"
  },
  {
    /* disk_name    = "tf-bms-disk-dev-swap-" */
    /* device_name  = "tf-bms-disk-dev-swap-" */
    auto_delete  = true
    boot         = false
    disk_size_gb = "32"
    disk_type    = "pd-balanced"
  },
  {
    auto_delete  = true
    boot         = false
    disk_size_gb = "10"
    disk_type    = "pd-balanced"
  },
  {
    auto_delete  = true
    boot         = false
    disk_size_gb = "10"
    disk_type    = "pd-balanced"
  }
  ]
}

variable "gce_inst_desc" {
  type        = string
  description = "Instance GCE description"
  default     = "GCE instance for migScaler application"
}

variable "gce_inst_template_name" {
  type        = string
  description = "Instance template for GCE (Non RAC)"
  default     = "migsc-single-template"
}

variable "gce_inst_template_rac_name" {
  type        = string
  description = "Instance template for GCE RAC"
  default     = "migsc-rac-template"
}

variable "gce_maintenance" {
  type        = string
  description = "Instance availability Policy"
  default     = "MIGRATE"
}

variable "gce_scope" {
  type        = list(string)
  description = "Scope of the GCE"
  default     = ["cloud-platform"]
}

variable "rac_option" {
  type        = bool
  default     = false
}

variable "gce_source_image" {
  type        = string
  description = "Image to provision de GCE"
  default     = null
}

variable "gce_count" {
  type        = number
  default     = null
}

variable "gce_machine_type" {
  type        = string
  description = "GCE Machine type"
  default     = "n2-standard-4"
}

variable "gcp_labels" {
  type = map
  default = {}
}
