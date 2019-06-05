# project name and id, used for resource provider configuration.
variable "project_name" {
  type        = "string"
  description = "GCP project name for the provider."
  default     = "airflow-sample"
}

variable "project_id" {
  type        = "string"
  description = "Globally unique project id."
}

variable "region" {
  default     = "europe-west1"
  description = "Default region for all terraform controlled resources."
}

variable "zone" {
  default     = "europe-west1-c"
  description = "Default zone for all terraform controlled resources."
}

variable "email" {
  type        = "string"
  description = "Owning email address for the GCP project."
}

variable "primary_nodes" {
  description = "Number of nodes in the kubernetes cluster underlying the Cloud Composer deployment."
  default     = 3
}
