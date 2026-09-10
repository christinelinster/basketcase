from dataclasses import dataclass
from functools   import lru_cache

import boto3
from botocore.exceptions import ClientError
import json

from dotenv import load_dotenv
import os

@dataclass(frozen=True, slots=True)
class Settings:
    pg_host: str
    pg_port: int
    pg_user: str
    pg_password: str
    pg_database: str
    mongodb_url: str
    mongodb_database: str
    host: str
    port: int
    environment: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()

    # AWS Credentials/Params
    aws_pg_credentials = get_aws_pg_credentials(os.getenv("AWS_PGSECRET")) or {}
    aws_mongo_url      = get_aws_mongo_credentials(os.getenv("AWS_MONGODB_SECRET")) or ''
    aws_pg_params      = get_aws_params(os.getenv("AWS_PGPARAMS_PATH")) or {}
    aws_mongo_params   = get_aws_params(os.getenv("AWS_MONGODB_PARAMS_PATH")) or {}

    return Settings(
        pg_host=aws_pg_params.get("host")              or os.getenv("PGHOST")           or "localhost",
        pg_port=int(aws_pg_params.get("port")          or os.getenv("PGPORT")           or "5432"),
        pg_user=aws_pg_credentials.get("username")     or os.getenv("PGUSER")           or "postgres",
        pg_password=aws_pg_credentials.get("password") or os.getenv("PGPASSWORD", ""),
        pg_database=aws_pg_params.get("database")      or os.getenv("PGDATABASE")       or "basketcase",

        mongodb_url=aws_mongo_url or os.getenv("MONGODB_URL") or "mongodb://localhost:27017",
        mongodb_database=aws_mongo_params.get("database") or os.getenv("MONGODB_DATABASE") or "basketcase",

        host=os.getenv("HOST") or "127.0.0.1",
        port=int(os.getenv("PORT") or "8000"),
        environment=(os.getenv("APP_ENV") or "production").strip().lower(),
    )


def get_aws_params(path: str, region_name: str = 'us-east-1'):
    if path is None:
        return None
    
    ssm = boto3.client('ssm', region_name=region_name)
    try:
        response = ssm.get_parameters_by_path(Path=path)
        # Remove path prefix (eg. /capstone/basketcase/pg/database -> database)
        params = response['Parameters']
    except ClientError as e:
        raise e

    parsed_params = { param['Name'].split('/')[-1] : param['Value'] for param in params }
    return parsed_params


def get_aws_pg_credentials(secret_name: str, region_name: str = 'us-east-1'):
    if secret_name is None:
        return None
    
    secret_name = secret_name
    region_name = region_name

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        secret_value = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(secret_value['SecretString'])
    return { 'username': secret['username'], 'password': secret['password'] }


# Return the entire MongoDB connection URL as a string
def get_aws_mongo_credentials(secret_name: str, region_name: str = 'us-east-1'):
    if secret_name is None:
        return None
    
    secret_name = secret_name
    region_name = region_name

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        secret_value = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    return secret_value['SecretString']
    
