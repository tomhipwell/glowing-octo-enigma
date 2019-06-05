#!/bin/bash -xe

PROJECT_ID="$(gcloud projects list --format="value(projectId)" --filter="name=${PROJECT_NAME}")"
gcloud config set project "$PROJECT_ID"

#get the cloud composer environment
LOCATION=europe-west1
COMPOSER_NAME=$(gcloud composer environments list --locations "${LOCATION}" --format="value(name)")
echo "Working with composer envrionment: $COMPOSER_NAME in project: $PROJECT_ID"
#deploy to the cloud composer environment
gcloud composer environments storage dags import \
        --environment "${COMPOSER_NAME}" \
        --location "${LOCATION}" \
        --source ./airflow/dags
