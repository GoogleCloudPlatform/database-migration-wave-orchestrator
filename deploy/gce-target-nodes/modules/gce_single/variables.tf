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

variable "rac_option" {
  type        = bool
  default     = false
}

variable "gce_count" {
  type        = string
  description = "Number of GCE to be provisioned"
  default     = 2
}

variable "gce_instance_name_rac" {
  type        = string
  description = "Real name of the GCE - RAC"
  default     = "migsc-vm-rac-"
}

variable "gce_instance_name_single" {
  type        = string
  description = "Real name of the GCE - Non RAC"
  default     = "migsc-vm-single-"
}

variable "project_id" {
  type        = string
  description = "Project where the GCE will be created"
  default     = "project_id"
}

variable "bms_gce_disks_shared" {
  description = "List of maps of additional disks. See https://www.terraform.io/docs/providers/google/r/compute_instance_template.html#disk_name"
  type = list(object({
    auto_delete  = bool
    boot         = bool
    disk_size_gb = number
    disk_type    = string
  }))
  default = [
  {
    disk_name    = "migsc-tf-disk-data-"
    device_name  = "migsc-tf-disk-data-"
    auto_delete  = true
    boot         = false
    disk_size_gb = "10"
    disk_type    = "pd-balanced"
  },
  {
    disk_name    = "migsc-tf-disk-reco-"
    device_name  = "migsc-tf-disk-reco-"
    auto_delete  = true
    boot         = false
    disk_size_gb = "10"
    disk_type    = "pd-balanced"
  },
  {
    disk_name    = "migsc-tf-disk-ocr-"
    device_name  = "migsc-tf-disk-ocr-"
    auto_delete  = true
    boot         = false
    disk_size_gb = "10"
    disk_type    = "pd-balanced"
  },
]
}

variable "gce_region" {
  type        = string
  description = "Region where the VM will be created"
  default     = "europe-west1"
}

variable "bms_gce_disks_single" {
  description = "List of maps of additional disks. See https://www.terraform.io/docs/providers/google/r/compute_instance_template.html#disk_name"
  type = list(object({
    auto_delete  = bool
    boot         = bool
    disk_size_gb = number
    disk_type    = string
  }))
  default = [
  {
    disk_name    = "migsc-tf-disk-data-"
    device_name  = "migsc-tf-disk-data-"
    auto_delete  = true
    boot         = false
    disk_size_gb = "10"
    disk_type    = "pd-balanced"
  },
  {
    disk_name    = "migsc-tf-disk-reco-"
    device_name  = "migsc-tf-disk-reco-"
    auto_delete  = true
    boot         = false
    disk_size_gb = "10"
    disk_type    = "pd-balanced"
  }
]
}

variable "gce_source_image-rac" {
  type        = string
  description = "Source image for RAC"
  default     = "bms-rac-epam-dev"
}

variable "gce_source_image-non-rac" {
  type        = string
  description = "Source image for non-RAC"
  default     = "rhel-cloud/rhel-7"
}

variable "gce_template_single"  {
  type        = string
  description = "Instance template for creating Non RAC Instances"
  default     = "migsc-single-template"
}

variable "rac_suffix" {
  type        = string
  description = "Suffix for RAC option"
  default     = "-rc"
}

variable "single_instance_suffix" {
  type        = string
  description = "Suffix for non-RAC option"
  default     = "-si"
}

variable "bms-type-record" {
  type        = string
  description = "DNS type record"
  default     = "A"
}

variable "gce_zone" {
  type        = string
  description = "Zone where GCE will be created"
  default     = "europe-west1-b"
}

variable "metadata_script" {
  type        = string
  description = "Metadata Script"
  default     = "modules/gce_single/gce_bms_metadata.sh"
}

variable "bucket_gce_metadata" {
  type        = string
  description = "Bucket on which the GCE metadata -JSON- will be stored"
  default     = ""
}

variable "google_compute_template" {
  type        = string
  description = "Google compute template"
  default     = ""
}

variable "var_template_single" {
  type        = string
  description = "Var template single"
  default     = ""
}

variable "public-network" {
  type        = string
  description = "Name of the public network"
  default     = null
}

variable "public-subnetwork" {
  type        = string
  description = "Name of the subnetwork"
  default     = null
}

variable "gce_inst_template_name" {
  type        = string
  description = "Name of the TF resource GCE Non RAC"
  default     = null
}

variable "gce_machine_type" {
  type        = string
  description = "GCE Machine type"
  default     = "n2-standard-4"
}

variable "impersonate_sa" {
    type      = bool
    default   = false
}

variable "sa_tf_impersonate" {
    type      = string
    default   = null
}

variable "create_duration_default" {
    type      = number
    default   = 0
}

variable "gcp_labels" {
  type = map
  default = {}
}
