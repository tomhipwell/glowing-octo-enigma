# we use the google beta tf provider so we can use python 3 with cloud composer.
provider "google-beta" {
  region  = "${var.region}"
  project = "${var.project_id}"
}

resource "google_project" "project" {
  name                = "${var.project_name}"
  project_id          = "${var.project_id}"
  auto_create_network = true
}

resource "google_project_services" "project" {
  project = "${google_project.project.project_id}"

  services = [
    "storage-component.googleapis.com",
    "deploymentmanager.googleapis.com",
    "replicapool.googleapis.com",
    "redis.googleapis.com",
    "replicapoolupdater.googleapis.com",
    "resourceviews.googleapis.com",
    "cloudtrace.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "oslogin.googleapis.com",
    "cloudbilling.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "containerregistry.googleapis.com",
    "bigquery-json.googleapis.com",
    "pubsub.googleapis.com",
    "storage-api.googleapis.com",
    "appengine.googleapis.com",
    "stackdriver.googleapis.com",
    "cloudfunctions.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudbuild.googleapis.com",
    "composer.googleapis.com",
  ]
}

resource "google_service_account" "terraform_admin" {
  account_id   = "terraform"
  display_name = "terraform"
  project      = "${google_project_services.project.project}"
}

resource "google_project_iam_member" "terraform_owner" {
  role    = "roles/owner"
  project = "${google_project_services.project.project}"
  member  = "serviceAccount:${google_service_account.terraform_admin.email}"

  lifecycle = {
    create_before_destroy = true
  }
}

resource "google_project_iam_member" "project_owner" {
  count   = "${var.email != "foo@bar.com" ? 1 : 0}"
  role    = "roles/owner"
  project = "${google_project_services.project.project}"
  member  = "email:${var.email}"

  lifecycle = {
    create_before_destroy = true
  }
}

resource "google_composer_environment" "airflow" {
  provider = "google-beta"
  name     = "${google_project_services.project.project}-airflow"
  project  = "${google_project_services.project.project}"
  region   = "${var.region}"

  config {
    node_count = "${var.primary_nodes}"

    node_config {
      zone         = "${var.zone}"
      machine_type = "n1-standard-1"
    }

    software_config {
      airflow_config_overrides {
        core-load_example = "False"
      }

      python_version = "3"

      pypi_packages {
        google-cloud-storage = ""
      }
    }
  }
}

resource "google_storage_bucket" "composer_store" {
  name     = "${google_project_services.project.project}-bucket"
  project  = "${google_project_services.project.project}"
  location = "EU"

  lifecycle_rule {
    action {
      type = "Delete"
    }

    condition {
      age = "7"
    }
  }
}
