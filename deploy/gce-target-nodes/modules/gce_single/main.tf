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

#
# GCP resource provisioning for GCEs - Single instances (to simulate BMS servers)
#

// Local variables

resource "time_sleep" "wait_seconds" {
  create_duration = "${local.create_duration}s"
}

resource "time_sleep" "wait_120_seconds" {
  create_duration = "120s"
}

# Local variables
locals {
  source_image_gce  = var.rac_option ? var.gce_source_image-rac : var.gce_source_image-non-rac
  gce_name          = var.rac_option ? var.gce_instance_name_rac : var.gce_instance_name_single
  suffix_gce        = var.rac_option ? var.rac_suffix : var.single_instance_suffix
  rac_disk_count    = length(var.bms_gce_disks_shared)
  single_disk_count = length(var.bms_gce_disks_single)
  create_duration   = var.rac_option ? var.create_duration_default : var.gce_count*120
  gcp_labels = { for key, value in var.gcp_labels : lower(key) => lower(value) }
}

resource "google_compute_instance_from_template" "bms-gce-single" {
  provider = google-beta
  count = var.rac_option ? 0 : var.gce_count //  gce_count = 2
  name    = "${local.gce_name}-${format("%02d", count.index + 1)}" // "bms-epam-gce${format("%02d", count.index + 1)}"
  labels  = var.gcp_labels
  zone    = var.gce_zone                                          // "eu-west1-b"
  project = var.project_id

  source_instance_template = module.gce_template_module.google_compute_template // "${gce_templates.google_compute_template}" // "${var.var_template_single}"
  metadata_startup_script  = "${file(var.metadata_script)}"
  metadata = {
     value_of_bucket = "${var.bucket_gce_metadata}"
     value_of_count = "${var.gce_count}"
     value_of_region = "${var.gce_region}"
  }
  service_account {
    scopes = ["cloud-platform"]
  }
}

resource "null_resource" "json_metadata" {
 provisioner "local-exec" {
   command = "/bin/bash modules/gce_single/build_json_metadata.sh"
   environment = {
      BUCKET = "${var.bucket_gce_metadata}"
   }
 }
 depends_on = [google_compute_instance_from_template.bms-gce-single,time_sleep.wait_seconds]
}

resource "null_resource" "send_json_metadata" {
 provisioner "local-exec" {
   command = "/bin/bash modules/gce_single/send_json_metadata.sh"
   environment = {
      BUCKET = "${var.bucket_gce_metadata}"
   }
 }
 depends_on = [null_resource.json_metadata,google_compute_instance_from_template.bms-gce-single,time_sleep.wait_120_seconds]
}

module "gce_template_module" {
    #--------------------
    # REQUIRED Parameters
    #--------------------
    source                   = "./gce_templates"

    project_id               = var.project_id
    gce_region               = var.gce_region
    gce_zone                 = var.gce_zone

    public-network           = var.public-network
    public-subnetwork        = var.public-subnetwork

    gce_inst_template_name   = var.gce_inst_template_name
    gce_machine_type         = var.gce_machine_type
}
