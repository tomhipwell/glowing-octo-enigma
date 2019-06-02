resource "random_id" "randomized_project_name" {
  byte_length = 2
  prefix      = "-"
}

module "composer" {
  source       = "./composer"
  project_name = "airflow-example"
  project_id   = "airflow-example${random_id.randomized_project_name.hex}"
  email        = "foo@bar.com"
}
