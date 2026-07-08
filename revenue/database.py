import pandas as pd
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.exc import InterfaceError

from dotenv import load_dotenv
import os

def get_credentials():
    load_dotenv()
    server_name = os.getenv("DB_SERVER")
    database_name = os.getenv("DB_DATABASE")
    return server_name, database_name


def import_sql_table(server,database,query):

    connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"  # Adjust driver version if needed
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
    # print(connection_string)
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    # print(connection_url)
    engine = create_engine(connection_url)
    try:
        with engine.begin() as cnxn:
            df = pd.read_sql(query, cnxn)
    except InterfaceError: print('\n\n\nERROR de CONEXIÓN de SQLAlchemy\n\n\n')

    return df


def fill_fees_query(database_name,ciudad,fecha_min,fecha_max):

    query = f""" -- transaction id, order id, date, amount
        SELECT 
            Tr.id 'ID transacción',
            Tr.order_id 'ID orden',
            CAST(Tr.event_at AS DATETIME) 'Fecha y hora',
            Tr.amount 'Monto'
        FROM 
            [{database_name}].[dbo].[{ciudad}_Transactions] Tr
        WHERE
            Tr.[group_id] = 'partner_fees' AND
            Tr.[event_at] >= '{fecha_min}' AND
            Tr.[event_at] <= '{fecha_max}'
        ORDER BY CAST(Tr.event_at AS DATETIME) DESC;"""
    
    return query