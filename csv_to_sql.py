import csv
import sqlite3
import sys



#http://www.sqlitetutorial.net/sqlite-python/create-tables/
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        #To use 8-bit bytestring
        conn.text_factory = str
        return conn
    except Error as e:
        print(e)

    return None

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = "osm_project.db"

    create_node_table = """CREATE TABLE IF NOT EXISTS node (
                            id INT PRIMARY KEY,
                            lat NUM,
                            lon NUM,
                            user TEXT,
                            uid INT,
                            version TEXT,
                            changeset INT,
                            timestamp TEXT
                            ); """

    create_node_tags_table = """CREATE TABLE IF NOT EXISTS node_tags (
                                id INT,
                                key TEXT,
                                value TEXT,
                                type TEXT
                                ); """

    create_way_table = """CREATE TABLE IF NOT EXISTS way (
                            id INT PRIMARY KEY,
                            user TEXT,
                            uid INT,
                            version TEXT,
                            changeset INT,
                            timestamp TEXT
                            ); """


    create_way_tags_table = """CREATE TABLE IF NOT EXISTS way_tags (
                            id INT,
                            key TEXT,
                            value TEXT,
                            type TEXT
                            ); """

    create_way_nodes_table = """CREATE TABLE IF NOT EXISTS way_nodes (
                                id INT,
                                node_id INT,
                                position INT
                                ); """

    conn = create_connection(database)

    if conn is not None:
        #Create tables
        create_table(conn, create_node_table)
        create_table(conn, create_node_tags_table)
        create_table(conn, create_way_table)
        create_table(conn, create_way_tags_table)
        create_table(conn, create_way_nodes_table)

    with open('nodes_tags.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == "id":
                continue
            conn.execute("INSERT INTO node_tags VALUES (?, ?, ?, ?)", (row[0], row[1], row[2], row[3]))

    with open('nodes.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == "id":
                continue
            conn.execute("INSERT INTO node VALUES (?, ?, ?, ?, ?, ?, ?, ?)", \
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

    with open('ways_tags.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == "id":
                continue
            conn.execute("INSERT INTO way_tags VALUES (?, ?, ?, ?)", (row[0], row[1], row[2], row[3]))

    with open('ways_nodes.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == "id":
                continue
            conn.execute("INSERT INTO way_nodes VALUES (?, ?, ?)", (row[0], row[1], row[2]))

    with open('ways.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == "id":
                continue
            conn.execute("INSERT INTO way VALUES (?, ?, ?, ?, ?, ?)", \
                (row[0], row[1], row[2], row[3], row[4], row[5]))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()






