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

#--------------------------------------------------------------------------
#
# Terraform modules to provision GCE (target nodes for Oracle installation)
#
#--------------------------------------------------------------------------

module "gce_single" {
    source                   = "./modules/gce_single"
 
    //--------------------
    // REQUIRED parameters
    //--------------------
    project_id               = "_PROJECT_ID_HERE_"
    gce_instance_name_single = "migsc-test-cycle"
    gce_count                = 2
    bucket_gce_metadata      = "_BUCKET_FOR_JSON_FILE_"
    public-network           = "migsc-vpc"
    public-subnetwork        = "migsc-vpc-subnet"
 
    //--------------------
    // OPTIONAL parameters
    //--------------------
    gce_inst_template_name   = "migsc-single-template"
    gce_machine_type         = "n2-standard-4"
    gce_region               = "europe-west1"
    gce_zone                 = "europe-west1-b"
    gcp_labels = {
        created_by  = "terraform"
        environment = "uat"
        app_name    = "migscaler"
        app_release = "mvp"
    }
 
    // SA FOR Terraform IMPERSONATION
    impersonate_sa           = false
    sa_tf_impersonate        = "sa-test-migscaler"
}
