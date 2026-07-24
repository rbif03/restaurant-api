import asyncio
import os
import logging

import boto3
from dotenv import load_dotenv
from fastapi import Request

from services.ssm import ssm_get_parameter

logger = logging.getLogger(__name__)

load_dotenv()

rds_client = boto3.client("rds")


def get_connstr() -> str:
    ENDPOINT = ssm_get_parameter("/restaurant-api/db/endpoint")
    PORT = ssm_get_parameter("/restaurant-api/db/port")
    USER = ssm_get_parameter("/restaurant-api/db/username")
    REGION = boto3.Session().region_name
    DBNAME = ssm_get_parameter("/restaurant-api/db/name")

    token = rds_client.generate_db_auth_token(
        DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION
    )
    logger.info("Obtained DB password.")
    connstr = (
        f"host={ENDPOINT} port={PORT} dbname={DBNAME} user={USER} password={token}"
    )
    return connstr


def get_db_conn(request: Request):
    return request.app.state.db_conn


if __name__ == "__main__":
    print(get_connstr())
