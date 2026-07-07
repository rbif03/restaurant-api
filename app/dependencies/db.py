import asyncio
import os

import boto3
from dotenv import load_dotenv
import psycopg

load_dotenv()

rds_client = boto3.client("rds")


def get_connstr() -> str:
    ENDPOINT = os.getenv("ENDPOINT")
    PORT = os.getenv("PORT")
    USER = os.getenv("USER")
    REGION = os.getenv("REGION")
    DBNAME = os.getenv("DBNAME")

    token = rds_client.generate_db_auth_token(
        DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION
    )

    connstr = (
        f"host={ENDPOINT} port={PORT} dbname={DBNAME} user={USER} password={token}"
    )
    print("connstr generated")
    return connstr


async def get_db():
    print("get_db called")
    connstr = await asyncio.to_thread(get_connstr)
    db = await psycopg.AsyncConnection.connect(connstr)
    print("connection established")
    try:
        yield db
    finally:
        print("db connection closure started")
        await db.close()
        print("db connection closed")


if __name__ == "__main__":
    print(get_connstr())
