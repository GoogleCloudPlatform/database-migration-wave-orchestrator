

data "google_app_engine_default_service_account" "default" {
  depends_on = [google_project_service.gcp_services]
}

# grant access to secret manager for application
resource "google_secret_manager_secret_iam_member" "secret-access" {
  secret_id = google_secret_manager_secret.db_conn_string.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.waverunner.email}"
}


resource "google_app_engine_application" "app" {
  project     = var.project_id
  location_id = var.app_engine_location
  iap {
    enabled              = true
    oauth2_client_id     = google_iap_client.project_client.client_id
    oauth2_client_secret = google_iap_client.project_client.secret
  }
}

resource "google_app_engine_flexible_app_version" "waverunner" {
  version_id = "v1"
  project    = var.project_id
  service    = "default"
  runtime    = "custom"

  network {
      name =  var.networkname
      subnetwork = var.subnetname
  }


  deployment {
    container {
      image = var.waverunner_image
    }
  }

  liveness_check {
    path = "/"
  }

  readiness_check {
    path = "/"
  }
  manual_scaling {
    instances = 2
  }

  env_variables = {
    #TODO: improve this
    DATABASE_URL = "postgresql+psycopg2://${var.user_name}:${random_password.db_user_pass.result}@/${var.db_name}?host=/cloudsql/${var.project_id}:${var.region}:${module.sql-db.instance_name}"
    # port = "8080"
    GCS_BUCKET                   = google_storage_bucket.bucket.name
    GCS_ORACLE_BINARY_PREFIX     = ""
    GCS_DEPLOYMENT_CONFIG_PREFIX = "ansible_config-test"
    USE_GCLOUD_LOGGING           = "TRUE"
    GCS_PUBSUB_TOPIC             = "projects/${var.project_id}/topics/${google_pubsub_topic.topic.0.name}"
    GCP_PUBSUB_TOPIC             = "projects/${var.project_id}/topics/${google_pubsub_topic.topic.0.name}"
    GCP_PROJECT_NAME             = var.project_id
    GCP_SERVICE_ACCOUNT          = data.google_app_engine_default_service_account.default.email
    GCP_PROJECT_NUMBER           = data.google_project.project.number
    GCP_CLOUD_TASKS_QUEUE        = "projects/${var.project_id}/locations/${var.region}/queues/${google_cloud_tasks_queue.migsc-ctq.name}"
    GCP_CLOUD_RUN_SERVICE_NAME   = "" #projects/${var.project_id}/locations/${var.region}/services/${var.migsc_cloudrun_appl_name}-${random_string.random.result}"
    GCP_OAUTH_CLIENT_ID          = google_iap_client.project_client.client_id
    GCP_LB_URL                   = "" #https://${var.site_domain_name}"
  }
  beta_settings = {
    cloud_sql_instances = module.sql-db.instance_connection_name
  }


  noop_on_destroy = true

  timeouts {
    create  = "1h"
    update  = "1h"
    delete  = "20m"
  }

   lifecycle {
        ignore_changes        =  [ deployment ]
  }

  depends_on = [google_project_service.gcp_services]
}




resource "google_iap_app_engine_service_iam_member" "access_list" {
  for_each = toset(var.access_users)
  project  = var.project_id
  app_id   = google_app_engine_flexible_app_version.waverunner.project
  service  = google_app_engine_flexible_app_version.waverunner.service
  role     = "roles/iap.httpsResourceAccessor"
  member   = each.key
}
