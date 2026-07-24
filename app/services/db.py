import asyncio
import os
import logging

import boto3
from dotenv import load_dotenv
from fastapi import Request

logger = logging.getLogger(__name__)

load_dotenv()

rds_client = boto3.client("rds")


def get_connstr() -> str:
    ENDPOINT = os.getenv("ENDPOINT")
    PORT = os.getenv("PORT")
    USER = os.getenv("USERNAME")
    REGION = os.getenv("REGION")
    DBNAME = os.getenv("DBNAME")

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
