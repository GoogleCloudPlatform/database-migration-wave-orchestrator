module "gcp-foundation" {

  source = "./modules"

  #--------------------
  # REQUIRED Parameters
  #--------------------
  project_id = "atamrat-waverunner-test-2"

  // CLOUD IAP
  oauth_support_contact_email = "waverunner-dev@google.com"

  access_users = ["user:atamrat@google.com"]
  # access_users = ["group:waverunner-dev@google.com"]

  #--------------------
  # OPTIONAL Parameters
  # --------------------

  region = "us-central1"
  zone   = "us-central1-b"

}
