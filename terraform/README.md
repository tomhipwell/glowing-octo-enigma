# Terraform

## Billing

This project uses billed features on GCP. If you don't want to be charged, remember to tear down the environment once you are done with your development. If you'd like to enable billing, see the subsection below ('Enabling Billing').

Note terraform apply will fail the first time it is run unless billing is enabled for the project you create.

## Getting Started

Temporaily set your gcloud credentials gcloud auth application-default login:

```shell
gcloud auth application-default login
```

The above command will also print to std out a path to a json file, set the google application credentials environment variable used by terraform:

```shell
export GOOGLE_APPLICATION_CREDENTIALS=~/path/to/my/credentials.json
```

Set your working directory to ./terraform and run:

```shell
terraform init
```

This writes a terraform statefile locally on your machine. Note, if you want to productionize this codebase, you might want to move your stafile to be stored in a Cloud Storage Bucket, as then you can put in place a locking mechanism in place to prevent conflicts created by multiple peeps working on the codebase at the same time (see the subsection, "Backend").

If you've previously init'd your dir locally, make sure you run:

```shell
terraform refresh
```

To update your local state before starting work.

Once you've made your changes, run:

```shell
terraform plan
```

Which creates a plan object for what will happen when your changes get applied. Review your changes carefully - plan works by comparing the GCP project state to that defined in your code. If you're happy with the changes that will be made, then run:

```shell
terraform apply
```

This will apply your changes in the environment you have selected. Note that terraform is built around the concept of immutable infrastructure. So if your resources already exist, they will always be set to the state defined in code. This means that if you go and make a manual change to a GCP project through the Cloud Console those changes will be lost the next time terraform apply is run.

Bear in mind that Cloud Composer also takes a _long_ time to deploy due to the dependencies it needs to go and set up under the hood. So be patient.

## Enabling Billing

The terraform apply will fail the first time that you run the terraform codebase. This is because billing will not be enabled for the project you create. You can enable billing from the command line. First, check that you have a billing account configured:

```shell
# list your billing accounts
gcloud alpha billing accounts list
```

If you don't use your google foo to figure out how to do this. Once you have a billing account configured, link it to your project:

```shell
# list your projects
gcloud projects list
# link your project
gcloud alpha billing projects link my-project \
      --billing-account 0X0X0X-0X0X0X-0X0X0X
```

This can also be done directly in terraform so that your terraform apply works first time. Just adjust the project resource block to include a billing attribute as follows (note the removal of the lifecycle block):

```terraform
data "google_billing_account" "acct" {
  display_name = "my-billing-account"
  open         = true
}

resource "google_project" "project" {
  name                = "${var.project_name}"
  project_id          = "${var.project_id}"
  billing_account     = "${data.google_billing_account.acct.id}"
  auto_create_network = true
}
```

## Outputs

You can get output variables from Terraform using the command:

```shell
terraform output
```

This will give you the project name, id and the id of the cloud composer environment (useful if you want to work with the gcloud CLI).

## Switching to a service account when using terraform

Once you've setup your initial project, you can then switch to using a service account that gets setup as part of the GCP project to administer it.

```shell
export PROJECT_ID=my-project-id
gcloud iam service-accounts keys create key.json
    --iam-account=terraform@"$PROJECT_ID".iam.gserviceaccount.com
export GOOGLE_APPLICATION_CREDENTIALS=key.json
```

You can also switch to use the service account your shell (useful for testing):

```shell
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
```

## Backend

The sample code is intended as a lightweight demo project. If you want to industrialise it, I'd suggest creating a dedicated terraform project to host a service account which has rights to create/destroy projects within your organsation, and also a storage bucket which you can use as a backend for your terraform state file. Use your google foo to find instructions on how to do this, then just add a backend block to the main.tf and you should be away:

```terraform
terraform {
  backend "gcs" {
    bucket  = "my-terraform-admin-bucket"
    prefix  = "terraform/state"
    project = "my-terraform-admin-project"
  }
}
```

## Destroy

Proceed with caution, but you can tear down a test environment by using:

```shell
terraform destroy
```

## Debugging

You can debug the terraform code by setting the \$TF_LOG and TF_LOG_PATH env vars. There are four main log levels - ERROR, DEBUG, TRACE, INFO. If you use DEBUG, http requests are logged with host/endpoint/request.

```shell
export TF_LOG=DEBUG
```

## Viewing the Terraform Graph

Terraform is using a DAG behind the scenes to map the relationship between the resources you have defined. It's important to understand how this is hanging together, as it impacts how terraform will go deploy your changes at apply time. You can view this graph with the command:

```shell
terraform graph
```

If you have graphviz on your machine, you can visualise the graph:

```shell
terraform graph | dot -Tpng > graph.png
```

The terraform graph is always computed on the fly from your local configurations files, so checking this quickly after you have completed your code changes is a good post-release step.
