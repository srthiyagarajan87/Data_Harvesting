import mysql.connector
import configparser

config = configparser.ConfigParser()
config.read('ytharvesting.conf')

# Database connection settings


#conn = None
# Establish a connection to the database
def DBConnect():
    
    try:
        print("Connecting to the database...")
        conn = mysql.connector.connect(
            username = config['Database']['username'],
            password = config['Database']['password'],
            host = config['Database']['host'],
            database = config['Database']['database']
        )
        
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")

    return conn    
    #if conn.is_connected():
    #    return True
    #else:
    #    return False
def DBDisconnect(conn):
    conn.close()

# Execute Insert/Update DB queries
def insertintoDB(conn, query, data):
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Insert data into a table
    #query = "INSERT INTO your_table (name, email) VALUES (%s, %s)"
    #data = ('John Doe', 'john.doe@example.com')
    try:
        affected_rows = cursor.executemany(query, data)
        conn.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062:
            print(f"Found Duplicate entry... : {err}")
            return err.errno
        else:
            print(f"Error inserting data into the database: {err}")
            return 0
    print(f"Inserted {affected_rows} rows into the database.")
    return 1

# Commit the changes
#cnx.commit()
def selectfromDB(conn, query, data):
    rows = None
    try:
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        cursor.execute(query, data)
        rows = cursor.fetchall()
        cursor.close()
        #conn.commit()
    except mysql.connector.Error as err:
        print(f"Error selecting data from the database: {err}")
        return False
    return rows

# Select data from the table
#query = "SELECT * FROM your_table"
#cursor.execute(query)

# Fetch all the rows


# Print the rows
#for row in rows:
 #   print(row)

# Close the cursor and connection
#cursor.close()
#cnx.close()