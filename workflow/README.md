# Airflow

## Getting Started

Ensure you're using python 3.7.3:

```shell
python --version`
```

Create a python virtual environment:

```shell
python3 -m venv .env
```

Activate it: `

```shell
# you can deactivate with `deactivate`
source .env/bin/activate
```

To get Airflow up and running locally, first set the AIRFLOW_HOME environment variable:

```shell
# use an absolute file path here rather than a relative path, where workspace is pwd, and assuming you are in the right directory :)
export AIRFLOW_HOME=$(pwd)
```

Install apache-airflow with the correct dependencies. We use LocalExecutor for task execution and postgres as our backend when testing locally:

```shell
export SLUGIFY_USES_TEXT_UNIDECODE=yes
pip3 install apache-airflow[postgres]
```

We've written a docker-compose file which will start a container running postgres to use as our backend. From the root directory of the project, run:

```shell
docker-compose up -d
```

Switch into the airflow subdirectory and then initialize the database:

```shell
cd ./workflow
airflow initdb
```

You should see a airflow.cfg file created at this point in your home directory. Within this, edit the airflow.cfg so that your configuration points to the correct directories containing your dags, logs and plugins. Most imporatantly, edit the sql alchemy connection string to point to your postgres instance:

```shell
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost/airflow
```

While you're there, also stop the examples from loading and don't pickle our xcoms.

```shell
load_examples = False
enable_xcom_pickling = False
```

Once this is done, reset the airflow database and re-init:

```shell
airflow resetdb
airflow initdb
```

Set the variables required to run the DAG without your tasks erroring:

```shell
airflow variables -s airflow_project my-gcp-project-name
airflow variables -s airflow_bucket my-gcs-bucket-name
```

Start the webserver, default port is 8080:

```shell
airflow webserver -p 8080
```

Then just head to localhost 8080. Add any variables which are defined in our DAG via the admin menu.

Start the scheduler:

```shell
airflow scheduler
```

List all the loaded dags:

```shell
airflow list_dags
```

List the tasks associated with a dag:

```shell
airflow list_tasks sample
```

Run a sample task to try it out:

```shell
airflow test sample select_filename 2019-05-31
```
