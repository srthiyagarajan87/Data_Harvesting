import streamlit as st
import googleapiclient.discovery
import googleapiclient.errors
import globals as g
import configparser 
import DBConnect as db

def main():
    init()
    pg = st.navigation([st.Page("Home.py", title="Home"), st.Page("YT-Harvesting.py", title="Harvest Data"), st.Page("reports.py", title="Report")])
    pg.run()

def init():
    config = configparser.ConfigParser()
    config.read('ytharvesting.conf')

    try:
        api_service_name = config["YouTube"]["api_service_name"]
        api_version = config["YouTube"]["api_version"]
        g.youtube=googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=config["YouTube"]["developerKey"])
    except Exception as e:
        print ("Failed to connect to YouTube API", e)
        return
    
    g.conn = db.DBConnect()
    if g.conn.is_connected():
        print("Connected to MySQL database")
    else:
        print("Failed to connect to MySQL database")
        return

if __name__ == "__main__":
    main()