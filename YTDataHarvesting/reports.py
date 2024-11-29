import streamlit as st
import pandas as pd
import DBConnect as db

REPORT1 = "What are the names of all the videos and their corresponding channels?"
REPORT2 = "Which channels have the most number of videos, and how many videos do they have?"
REPORT3 = "What are the top 10 most viewed videos and their respective channels?"
REPORT4 = "How many comments were made on each video, and what are their corresponding video names?"
REPORT5 = "Which videos have the highest number of likes, and what are their corresponding channel names?"
REPORT6 = "What is the total number of likes and dislikes for each video, and what are their corresponding video names?"
REPORT7 = "What is the total number of views for each channel, and what are their corresponding channel names?"
REPORT8 = "What are the names of all the channels that have published videos in the year 2022?"
REPORT9 = "What is the average duration of all videos in each channel, and what are their corresponding channel names?"
REPROT10 = "Which videos have the highest number of comments, and what are their corresponding channel names?"

QUERY1 = "select ch.channel_name channel_name, vi.video_name video_name from channel_details ch, playlist pl, video_details vi where ch.channel_id = pl.channel_id and pl.playlist_id = vi.playlist_id;"
QUERY2 = "select channel_id, channel_name, count(channel_id) as video_count from (select video_id, pl.playlist_id, ch.channel_id, ch.channel_name from channel_details ch, video_details vi, playlist pl where vi.playlist_id = pl.playlist_id and pl.channel_id = ch.channel_id) as info group by channel_id order by video_count desc limit 1;"
QUERY3 = "select channel_name, video_name, view_count from video_details vi, playlist pl, channel_details ch where vi.playlist_id = pl.playlist_id and pl.channel_id = ch.channel_id order by view_count desc limit 10;"
QUERY4 = "select video_name, count(comment_id) as comment_count from video_details vi, comment_details co where vi.video_id = co.video_id group by video_name order by comment_count;"
QUERY5 = "select channel_name, video_name, like_count from video_details vi, playlist pl, channel_details ch where vi.playlist_id = pl.playlist_id and pl.channel_id = ch.channel_id order by like_count desc limit 1;"
QUERY6 = "select video_name, like_count, dislike_count from video_details order by video_name;"
QUERY7 = "select channel_name, channel_views from channel_details order by channel_views desc;"
QUERY8 = "select channel_name, video_name from channel_details ch, video_details vi, playlist pl where year(published_date) = 2022 and vi.playlist_id = pl.playlist_id and pl.channel_id = ch.channel_id;"
QUERY9 = "select channel_name, avg(duration) from channel_details ch, video_details vi, playlist pl where vi.playlist_id = pl.playlist_id and pl.channel_id = ch.channel_id group by channel_name;"
QUERY10 = "select ch.channel_name, vi.video_name, vd.count from channel_details ch, playlist pl, video_details vi, (select vi.video_id videoid, count(comment_id) count from video_details vi, comment_details co where vi.video_id = co.video_id group by videoid order by comment_count desc limit 1) as vd where vd.videoid = vi.video_id and vi.playlist_id = pl.playlist_id and pl.channel_id = ch.channel_id;"

HEADER1 = ["Channel Name", "Video Name"]
HEADER2 = ["Channel Id", "Channel Name", "Video Count"]
HEADER3 = ["Channel Name", "Video Name", "View Count"]
HEADER4 = ["Video Name", "Comment Count"]
HEADER5 = ["Channel Name", "Video Name", "Likes Count"]
HEADER6 = ["Video Name", "Likes Count", "Dislikes Count"]
HEADER7 = ["Channel Name ", "Channel Views"]
HEADER8 = ["Channel Name", "Video Name"]
HEADER9 = ["Channel Name", "Average Duration"]
HEADER10 = ["Chennal Name", "Video Name", "Comment Count"]
st.title("Reports")


def main():
    print("Inside Reports")

    global conn 
    conn = db.DBConnect()
    if conn.is_connected():
        print("Connected to MySQL database")
    else:
        print("Failed to connect to MySQL database")
        return

    options = [REPORT1, REPORT2, REPORT3, REPORT4, REPORT5, REPORT6, REPORT7, REPORT8, REPORT9, REPROT10]
    selected_report = st.selectbox("Select a report", options, index=None)
    if selected_report:
        on_select(selected_report)


def on_select(selected_report):
    st.write("You selected:", selected_report)

    if selected_report == REPORT1:
        show_report(QUERY1, HEADER1)
    elif selected_report == REPORT2:
        show_report(QUERY2, HEADER2)
    elif selected_report == REPORT3:
        show_report(QUERY3, HEADER3)
    elif selected_report == REPORT4:
        show_report(QUERY4, HEADER4)
    elif selected_report == REPORT5:
        show_report(QUERY5, HEADER5)
    elif selected_report == REPORT6:
        show_report(QUERY6, HEADER6)
    elif selected_report == REPORT7:
        show_report(QUERY7, HEADER7)
    elif selected_report == REPORT8:
        show_report(QUERY8, HEADER8)
    elif selected_report == REPORT9:
        show_report(QUERY9, HEADER9)
    elif selected_report == REPROT10:
        show_report(QUERY10, HEADER10)


def show_report(query, header):
    results =db.selectfromDB(conn, query, None)
    if results is None:
        st.write("No records match this query")
        return
  
    # Create a Pandas dataframe from the results
    reportdf = pd.DataFrame(results, columns=header)
    reportdf.index = range(1, 1 + len(reportdf))
    #reportdf[["channel_name", "video_name"]].style.set_table_styles([{'selector': 'th', 'props': ['font-weight', 'bold']}])
    #reportdf.style.set_table_styles([{'selector': 'th', 'props': ['font-weight', 'bold']}])
    st.table(reportdf)


#if __name__ == "__main__":
main()