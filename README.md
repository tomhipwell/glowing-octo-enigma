# glowing-octo-enigma

Everything you need to get started with developing on Airflow. This means sample Airflow DAGs and operators plus Terraform code to deploy a Cloud Composer environment on GCP, a deploy script you could hook into a CD pipeline, bundled documentation and sample tests. Written for the Python London meetup.

## Getting Started

You'll need to install terraform, python, docker and the gcloud SDK.

```shell
brew install terraform
brew install python
brew install docker
brew cask install google-cloud-sdk
```

## Workflow

Airflow related code, including a sample DAG and just enough information to get started with local development.

## Terraform

All the code you need to deploy your Cloud Composer environment on GCP, plus instructions on how to do it.

## Scripts

Bash scripts to deploy your Airflow DAG/Hooks/Operators to your Cloud Composer environment.
