from sqlalchemy import create_engine

# Sets mysql connection
def set_connection(user, passwd, host, db, port='3306'):
    """"""
    # MySQL-database connection string
    DB_URI = "mysql://{user}:{passwd}@{host}:{port}/{db}"
    engine = create_engine(DB_URI.format(
        user   = user,
        passwd = passwd,
        host   = host,
        port   = port,
        db     = db)
    )

    return engine
