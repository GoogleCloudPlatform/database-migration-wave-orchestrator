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
