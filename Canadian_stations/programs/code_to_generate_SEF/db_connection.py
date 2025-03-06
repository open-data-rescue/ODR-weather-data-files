# -*- coding: utf-8 -*-
import pymysql
import sqlalchemy
from sqlalchemy import URL
import os


def connect(cfg):
    # if "db" not in cfg:
    # ECCC server database
    ## dbHost = os.getenv("ECCC_db_host")
    ## dbPort = int(os.getenv("ECCC_db_port"))
    ## dbUser = os.getenv("ECCC_db_user")
    ## dbPasswd = os.getenv("ECCC_db_passwd")
    ## dbDB = os.getenv("ECCC_db_database")

    # # server
    # dbHost = "54.39.21.6"
    # dbPort = 3306
    # dbUser = "mysql"
    # dbPasswd = "3589a8dea043af14"
    # dbDB = "eccc_db"

    # localhost
    dbHost = os.getenv("localhost")
    dbPort = 3306
    dbUser = os.getenv("db_root")
    dbPasswd = os.getenv("db_password_root")
    dbDB = "Canada_wx"
    # else:
    #     dbHost = cfg["db"]["host"]
    #     dbPort = cfg["db"]["port"]
    #     dbUser = cfg["db"]["user"]
    #     dbPasswd = cfg["db"]["password"]
    #     dbDB = cfg["db"]["database"]

    # connecting to online DB

    mydb = pymysql.connect(
        host=dbHost,
        port=dbPort,
        user=dbUser,
        password=dbPasswd,
        database=dbDB
        )

    url = URL.create(
        "mysql+mysqlconnector",
        username=dbUser,
        host=dbHost,
        port=dbPort,
        password=dbPasswd,
        database=dbDB
        )

    engine = sqlalchemy.create_engine(url)

    return (mydb, mydb.cursor(), engine)
