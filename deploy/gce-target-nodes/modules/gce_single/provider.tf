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

#------------------------------------------------------------------------------------------------
#
# This file contains the code to impersonate the service account for Terraform provisioning
#
# The same code allows terraform to execute with no service account impersonation mode
#------------------------------------------------------------------------------------------------

locals {
 terraform_service_account = var.impersonate_sa ? "${var.sa_tf_impersonate}@${var.project_id}.iam.gserviceaccount.com" : null
}

provider "google" {
 alias  = "impersonation"
 scopes = var.impersonate_sa ? [
   "https://www.googleapis.com/auth/cloud-platform",
   "https://www.googleapis.com/auth/userinfo.email",
 ] : null
 project = var.project_id
 region  = var.gce_region
}

provider "google-beta" {
 alias  = "impersonation"
 scopes = var.impersonate_sa ? [
   "https://www.googleapis.com/auth/cloud-platform",
   "https://www.googleapis.com/auth/userinfo.email",
 ] : null
 project = var.project_id
 region  = var.gce_region
}

data "google_service_account_access_token" "google-default" {
 count = var.impersonate_sa ? 1 : 0
 provider               	= google.impersonation
 target_service_account 	= local.terraform_service_account
 scopes                 	= ["userinfo-email", "cloud-platform"]
 lifetime               	= "1200s"
}

data "google_service_account_access_token" "google-beta-default" {
 count = var.impersonate_sa ? 1 : 0
 provider               	= google-beta.impersonation
 target_service_account 	= local.terraform_service_account
 scopes                 	= ["userinfo-email", "cloud-platform"]
 lifetime               	= "1200s"
}

provider "google" {
 access_token    = var.impersonate_sa ? data.google_service_account_access_token.google-default.0.access_token : null
 request_timeout = var.impersonate_sa ? "60s" : null
 project         = var.project_id
 region          = var.gce_region
}

provider "google-beta" {
 access_token    = var.impersonate_sa ? data.google_service_account_access_token.google-beta-default.0.access_token : null
 request_timeout = var.impersonate_sa ? "60s" : null
 project         = var.project_id
 region          = var.gce_region
}
