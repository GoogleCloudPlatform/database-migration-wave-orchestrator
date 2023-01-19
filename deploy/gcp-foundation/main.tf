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

  source = "./modules"

  #--------------------
  # REQUIRED Parameters
  #--------------------
  project_id = "<<<Google Project Name>>>"
  #project_id = "waverunner"

  // CLOUD IAP
  oauth_support_contact_email = "<<<support email>>>"
  #oauth_support_contact_email = "waverunner-dev@google.com"

  access_users = ["user:<<<useremail>>>"]
  # access_users = ["group:waverunner-dev@google.com"]
  # access_users = ["user:user@google.com"]

  #--------------------
  # OPTIONAL Parameters
  # --------------------

  region = "<<<region>>>"
  #region = "us-central1"
  zone   = "<<<zone>>>"
  #zone   = "us-central1-b"

}
