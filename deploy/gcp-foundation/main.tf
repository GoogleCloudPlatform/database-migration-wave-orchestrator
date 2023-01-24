module "gcp-foundation" {

  source = "./modules"

  #--------------------
  # REQUIRED Parameters
  #--------------------
  project_id = "projectid123"

  // CLOUD IAP
  oauth_support_contact_email = "user1@google.com"

  access_users = ["user:user2@google.com","user:user3@google.com"]

  subnetname="sharedsubnet"
  networkname="sharedvpc"

  #--------------------
  # OPTIONAL Parameters
  # --------------------

  region = "us-central1"
  zone   = "us-central1-b"

}
