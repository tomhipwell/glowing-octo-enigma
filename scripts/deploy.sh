#!/bin/bash -xe

#authenticate the service account
gcloud auth activate-service-account --key-file "$GOOGLE_APPLICATION_CREDENTIALS"
PROJECT_ID="$(gcloud projects list --format="value(projectId)" --filter="name=${PROJECT_NAME}")"
gcloud config set project "$PROJECT_ID"

#get the cloud composer environment
LOCATION=europe-west1
COMPOSER_NAME=$(gcloud composer environments list --locations "${LOCATION}" --format="value(name)")

#deploy to the cloud composer environment
gcloud composer environments storage dags import \
        --environment "${COMPOSER_NAME}" \
        --location "${LOCATION}" \
        --source ../airflow
