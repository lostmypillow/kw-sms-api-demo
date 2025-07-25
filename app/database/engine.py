import os

import pyodbc
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

pyodbc.pooling = False

connection_url = URL.create(
    "mssql+aioodbc",
    username=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    query={"driver": "ODBC Driver 18 for SQL Server", "TrustServerCertificate": "yes"},
)

async_engine = create_async_engine(
    connection_url,
    pool_size=100,
    max_overflow=0,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)