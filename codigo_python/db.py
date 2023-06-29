import psycopg2
from decouple import config


def open_connection():

    return psycopg2.connect(

        host=config("PGHOST").__str__(),

        database=config("PGDATABASE").__str__(),

        user=config("PGUSER").__str__(),

        port=config("PGPORT").__str__(),

        password=config("PGPASSWORD").__str__()

    )

def mail():
    return config("MAIL").__str__()


def passmail():
    return config("PASSMAIL").__str__()

def execute_insert_update(sql):

    try:

        conn = open_connection()

        cur = conn.cursor()

        cur.execute(sql)

        conn.commit()

        cur.close()

        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:

        print(error)

        raise error

    finally:

        if conn is not None:

            conn.close()


def execute_update(sql):

    try:

        conn = open_connection()

        cur = conn.cursor()

        cur.execute(sql)

        conn.commit()

        cur.close()

        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:

        print(error)

        raise error

    finally:

        if conn is not None:

            conn.close()


def execute_select(sql):

    try:

        conn = open_connection()

        cur = conn.cursor()

        cur.execute(sql)

        sqlResult = cur.fetchall()

        cur.close()

        return sqlResult

    except (Exception, psycopg2.DatabaseError) as error:

        print(error)

        raise error

    finally:

        if conn is not None:

            conn.close()
