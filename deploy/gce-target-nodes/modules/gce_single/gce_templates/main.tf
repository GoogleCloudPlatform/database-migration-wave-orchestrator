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
# Instance template creation for GCE (Single instance and RAC installation)
#

# Local variables
locals {
  source_image_gce = var.rac_option ? var.gce_source_image-rac : var.gce_source_image-non-rac
}

resource "google_compute_address" "bms-gce-static" {
  name        = var.bms_gce_addressing_type
  project     = var.project_id
  region      = var.gce_region
}

resource "google_compute_instance_template" "bms-gce-single-tpl" {
  name        = var.gce_inst_template_name // var.gce_inst_template_name${local.suffix_gce}
  labels      = var.gcp_labels
  description = var.gce_description
  project     = var.project_id
  region      = var.gce_region

  instance_description = var.gce_inst_desc
  machine_type         = var.gce_machine_type
  can_ip_forward       = var.gce_can_ip_forward

  scheduling {
    automatic_restart   = var.gce_autom_restart // true
    on_host_maintenance = var.gce_maintenance   // "MIGRATE"
  }

  disk {
    source_image = local.source_image_gce // data.google_compute_image.rac_image.self_link // var.gce_source_image // "rhel-7-v20211105"
    auto_delete  = var.gce_auto_delete  // true
    boot         = var.gce_disk_boot    // true
    disk_size_gb = var.gce_disk_size    // "20"
    disk_type    = var.gce_disk_type    // "pd-balanced"
  }

  dynamic "disk" {
    for_each = var.bms_gce_common_disks
    content {
      auto_delete  = disk.value["auto_delete"]
      boot         = disk.value["boot"]
      disk_size_gb = disk.value["disk_size_gb"]
      disk_type    = disk.value["disk_type"]
    }
  }

  network_interface {
    network    = var.public-network
    access_config {
         nat_ip = google_compute_address.bms-gce-static.address
    }
    subnetwork = var.public-subnetwork
    subnetwork_project = var.project_id
  }

  service_account {
    scopes = var.gce_scope // ["cloud-platform"]
  }
}

//
// OUTPUT values
//

output "google_compute_template" {
  value = "${google_compute_instance_template.bms-gce-single-tpl.name}"
  description = "Google Compute tempate"
}
