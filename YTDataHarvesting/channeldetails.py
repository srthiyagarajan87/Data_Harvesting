# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
#import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import streamlit as st
import DBConnect as db
import pandas as pd
import isoduration as isod

st.set_page_config(page_title="page1.", layout="wide")
SUCCESS = "success"
FAILURE = "failure"

DUPLICATE_KEY_ERROR = 1062
INSERT_CHANNEL_DETAILS = "INSERT INTO channel_details (channel_id, Channel_Name, channel_type, channel_views, channel_description, channel_status) VALUES (%s, %s, %s, %s, %s, %s) on duplicate key update Channel_Name = VALUES(Channel_Name), channel_type = VALUES(channel_type), channel_views = VALUES(channel_views), channel_description = VALUES(channel_description), channel_status = VALUES(channel_status)"
INSERT_PLAYLIST_DETAILS = "INSERT INTO playlist (channel_id, playlist_id, playlist_name) VALUES (%s, %s, %s) on duplicate key update playlist_name = VALUES(playlist_name)"
INSERT_VIDEO_DETAILS = "INSERT INTO video_details (playlist_id, video_id, video_name, video_description, published_date, view_count, like_count, favorite_count, comment_count, duration, thumbnail, caption_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update video_name = VALUES(video_name), video_description = VALUES(video_description), published_date = VALUES(published_date), view_count = VALUES(view_count), like_count = VALUES(like_count), favorite_count = VALUES(favorite_count), comment_count = VALUES(comment_count), duration = VALUES(duration), thumbnail = VALUES(thumbnail), caption_status = VALUES(caption_status)"
INSERT_COMMENT_DETAILS = "INSERT INTO comment_details (video_id, comment_id, comment_text, comment_author, comment_published_date) VALUES (%s, %s, %s, %s, %s) on duplicate key update comment_text = VALUES(comment_text), comment_author = VALUES(comment_author), comment_published_date = VALUES(comment_published_date)"
#scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
#conn = None
youtube = None

channelList = []
playlistList = []
videoList = []
commentList = []
selectedchannelid = ""
def main():

    
    st.title("YouTube Data Harvesting")
    

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Connect to DB
    conn = db.DBConnect()
    #if db.DBConnect(conn):
    #    print("DB Connected successfully")
    #else:
    #    print("Failed to connect to database")
    #    return
    if conn.is_connected():
        print("Connected to MySQL database")
    else:
        print("Failed to connect to MySQL database")
        return
    api_service_name = "youtube"
    api_version = "v3"
    #client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

    # Get credentials and create an API client
    #flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
     #   client_secrets_file, scopes)
    #credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey="AIzaSyCONhnXcIezTGkkzQkwvH4u5IBFbIrOfNw")
    #channelid = None
    channelid = "UCUicT5osQLEL11TimsC8I1g"
    channeldetails(conn, youtube, channelid)

    # #Close DB connection
    db.DBDisconnect(conn)


def getallchannelinfo(youtube, channelid):
    
    #To get playlist details using channel id, query with playlist.

    playlistdetails(youtube, channelid)  

    if playlistList is not None:
        for playlist in playlistList:
            result = videolistdetails(youtube, playlist['Playlist Id'])
            if result is None:
                print("Error in getting video details")
                return None

    if videoList is not None:
        for video in videoList:
            result = commentdetails(youtube, video['Video Id'])
            if result is None:
                print("Error in getting comment details")
                return None

    return SUCCESS
    
# Function to get channel details:
# Channel Id, Channel Name, Channel_type, Channel_views, Channel_description and channel_status
#   
def channeldetails(conn,youtube, channelid):
    #channelid = "UCUicT5osQLEL11TimsC8I1g"
    try:
        chnrequest = youtube.channels().list(
            part="snippet,statistics,status",
            id=channelid
        )
        chnresponse = chnrequest.execute()
    except Exception as e:
        print("Error in getting channel details", e)
        st.write("Error in getting channel details")
        #deletechannel(channelid)
        return None
    

    try:
        chnsection = youtube.channelSections().list(
            part="snippet",
            channelId=channelid
        )
        chnsectionresponse = chnsection.execute()  

    except Exception as e:
        print("Error in getting channel section details", e)
        #st.write("Error in getting channel section details")
        #deletechannel(channelid)
        return None
    
    if chnsectionresponse.get('items') is None or chnresponse.get('items') is None:
        print("No channel details found")
        #channelDict[channelid] = None
        return None
 
    chnName = chnresponse['items'][0]['snippet']['title']
    chnType = chnsectionresponse['items'][0]['snippet']['type']
    chnViews = chnresponse['items'][0]['statistics']['viewCount']
    chnDescription = chnresponse['items'][0]['snippet']['description']
    chnStatus = chnresponse['items'][0]['status']['privacyStatus']

    channelDict = {"Channel Id" : channelid, "Channel Name" : chnName, "Channel Type" : chnType, "Channel Views" : chnViews, "Channel Description" : chnDescription, "Channel Status" : chnStatus}
    channelList.append(channelDict)
    print("****** new print *******")
    print(channelList)

    result = getallchannelinfo(youtube, channelid)
    if result is None:
        print("Error in getting channel details")
        st.write("Error in getting channel details")
        deletechannel(channelid)
        return

    return channelList

def getchannelid(index):
    if channelList is None or len(channelList) == 0:
        print("No channel details found")
        return None
    
    print ("index : ", index)
    print ("channelList[index]['Channel Id'] : ", channelList[index]['Channel Id'])
    selectedchannelid = channelList[index]['Channel Id']
    return selectedchannelid

# Function to get playlist details
# Channelid, Playlistid, Playlisttitle
def playlistdetails(youtube, channelid):

    try:
        request = youtube.playlists().list(
            part="snippet",
            channelId=channelid 
        )
        response = request.execute()
    except Exception as e:
        print("Error in getting playlist details", e)
        st.write("Error in getting playlist details")
        deletechannel(channelid)
        return None
    if response.get('items') is None:
        print("No playlist found")
        return None

    #playlistids = [id for id['id'] in response['items']]
    for items in response['items']:
        #playlistDict[channelid, items['id']] = (items['id'], items['snippet']['title'])
        playlistitems = {"Channel Id" : channelid, "Playlist Id" : items['id'], "Playlist Title" : items['snippet']['title']}
        playlistList.append(playlistitems)
    
    return playlistList

# Function to get video details
# Video id, playlist id, video name, video description, published_date, view count, like count, dislike_count, favourite_count, 
# comment_count, duration, thumb nail, caption_status

def videolistdetails(youtube, playlistid):
    try:
        vidrequest = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlistid
        )

        vidresponse = vidrequest.execute()
    except Exception as e:
        print("Error in getting playlist details", e)
        st.write("Error in getting video list")
        deletechannel(playlistid)
        return None
    
    if vidresponse.get('items') is None:
        print("No video found")
        return None

    videoidlists = []
    for items in vidresponse['items']:
        #videoid = items['snippet']['resourceId']['videoId']
        videoidlists.append(items['snippet']['resourceId']['videoId'])
    print(videoidlists)

    try:
        videodetailsreq = youtube.videos().list(
            part="snippet, statistics, contentDetails",
            #id=','.join(videoidlists)
            id = videoidlists
        )
        videodetailsres = videodetailsreq.execute()
    except Exception as e:
        print("Error in getting video details", e)
        #st.write("Error in getting video details")
        return None
    
    if videodetailsres.get('items') is None:
        print("No video details found")
        return None
    
   
    for items in videodetailsres['items']:

        parsed_duration = isod.parse_duration(items['contentDetails']['duration']).time
        duration_seconds = (parsed_duration.hours*3600 + parsed_duration.minutes*60 + parsed_duration.seconds)

        videoitems = {"Playlist Id" : playlistid, "Video Id" : items['id'], "Video Title" : items['snippet']['title'], 
                      "Video Description" : items['snippet']['description'], "Published Date" : items['snippet']['publishedAt'].strip('Z'),
                      "View Count" : items['statistics']['viewCount'], "Like Count" : items['statistics']['likeCount'], 
                      "Favourite Count" : items['statistics']['favoriteCount'], "Comment Count" : items['statistics']['commentCount'],
                      "Duration" : duration_seconds, "Thumbnail" : items['snippet']['thumbnails']['default']['url'],
                      "Caption" : items['contentDetails']['caption']}
        
        videoList.append(videoitems)
    
    return videoList

def commentdetails(youtube, videoid):
    try:
        commentrequest = youtube.commentThreads().list(
            part="snippet",
            videoId=videoid
        )
        commentresponse = commentrequest.execute()
    except Exception as e:
        print("Error in getting comment details", e)
        #st.write("Error in getting comment details")
        #deletechannel(videoid)
        return None
    
    if commentresponse.get('items') is None:
        print("No comments found")
        return None
    
    for items in commentresponse['items']:
        commentitems = {"Video Id" : videoid, "Comment Id" : items['id'], "Comment" : items['snippet']['topLevelComment']['snippet']['textOriginal'],
                        "Author Name" : items['snippet']['topLevelComment']['snippet']['authorDisplayName'], 
                        "Published Date" : items['snippet']['topLevelComment']['snippet']['publishedAt'].strip('Z')}
        commentList.append(commentitems)

    return commentList

def getplaylist(chennalid):
    filteredplaylist = []
    for playlist in playlistList:
        if playlist['Channel Id'] == chennalid:
            filteredplaylist.append(playlist)
    return filteredplaylist

def getvideo(playlist):
    filteredvideo = []
    for id in playlist:
        for video in videoList:
            if video['Playlist Id'] == id['Playlist Id']:
                filteredvideo.append(video)
    return filteredvideo

def getcomment(video):
    filteredcomment = []
    for id in video:
        for comment in commentList:
            if comment['Video Id'] == id['Video Id']:
                filteredcomment.append(comment)
    return filteredcomment


def deletechannel(channelid):

    for channel in channelList:
        if channel['Channel Id'] == channelid:
            for playlist in playlistList:
                if playlist['Channel Id'] == channel['Channel Id']:
                    for video in videoList:
                        if video['Playlist Id'] == playlist['Playlist Id']:
                            for comment in commentList:
                                if comment['Video Id'] == video['Video Id']:
                                    commentList.remove(comment)
                            videoList.remove(video)
                    playlistList.remove(playlist)    
            channelList.remove(channel)
    
    return

def savethischannel(conn, channelid, channeldf, playlistdf, videodf, commentdf):

    # chnexists = ytapi.channelexistsindb(conn, selectedchannelid)
    # if chnexists:
    #     st.write("Channel already exists in DB. ID :", selectedchannelid)
    #     return False

    print("Saving this channel")
    if channeldf is not None:
        selectedchannelframe = channeldf[channeldf["Channel Id"] == channelid]
        insertchannel = [tuple(row) for row in selectedchannelframe.to_numpy()]
        print("******* Channel ******")
        print(insertchannel)
        if insertchannel is not None:
            result = db.insertintoDB(conn, INSERT_CHANNEL_DETAILS, insertchannel)
            print ("result after insert is", result)
            if result == DUPLICATE_KEY_ERROR:
                st.write("Channel already exists in DB. ID :", channelid, color="red")
                print("Channel already exists in DB. ID :", channelid)
                conn.rollback()
                return False
            elif result == 0:
                conn.rollback()
                st.write("Failed to insert into DB")
                print("Failed to insert into DB")
                return False

    if playlistdf is not None:
        insertplaylists = [tuple(row) for row in playlistdf.to_numpy()]
        print("******* Playlist ******")
        print(insertplaylists)
        if insertplaylists is not None:
            success = db.insertintoDB(conn, INSERT_PLAYLIST_DETAILS, insertplaylists)
            if not success:
                conn.rollback()
                print("Failed to insert into DB")
                return False

    if videodf is not None:
        insertvideos = [tuple(row) for row in videodf.to_numpy()]
        print("******* Video ******")
        print(insertvideos)
        if insertvideos is not None:
            success = db.insertintoDB(conn, INSERT_VIDEO_DETAILS, insertvideos)
            if not success:
                conn.rollback()
                print("Failed to insert into DB")
                return False

    if commentdf is not None:
        insertcomments = [tuple(row) for row in commentdf.to_numpy()]
        print("******* Comment ******")
        print(insertcomments)
        if insertcomments is not None:
            success = db.insertintoDB(conn, INSERT_COMMENT_DETAILS, insertcomments)
            if not success:
                conn.rollback()
                print("Failed to insert into DB")
                return False
            
    conn.commit()
    return True

def saveallchannels(conn):
    channeltuple = playlisttuple = videotuple = commenttuple = ()

    for channel in channelList:
        channelid = channel['Channel Id']
        chnexists = channelexistsindb(conn, selectedchannelid)
        if chnexists:
            st.write("Channel already exists in DB. ID :", selectedchannelid)
            print("Skipping channel ID", selectedchannelid, "Channel already exists in DB.")
            continue

        channeltuple = tuple(channel.values())
        print ("channel data : ", channeltuple)
        if channeltuple is not None:
            success = db.insertintoDB(conn, INSERT_CHANNEL_DETAILS, channeltuple)
            if not success:
                conn.rollback()
                print("Failed to insert into DB")
                return
        playlisttuple = ()    
        for playlist in playlistList:
            if playlist['Channel Id'] == channelid:
                playlisttuple = playlisttuple + tuple(playlist.values())
                videotuple = ()
                for video in videoList:
                    if video['Playlist Id'] == playlist['Playlist Id']:
                        videotuple = videotuple + tuple(video.values())
                        commenttuple = ()
                        for comment in commentList:
                            if comment['Video Id'] == video['Video Id']:
                                commenttuple = commenttuple + tuple(comment.values())
                        print("comment data : ", commenttuple)
                        if commenttuple is not None:
                            success = db.insertintoDB(conn, INSERT_COMMENT_DETAILS, commenttuple)
                            if not success:
                                conn.rollback()
                                print("Failed to insert into DB")
                                return
                print("video data : ", videotuple)
                if videotuple is not None:
                    success = db.insertintoDB(conn, INSERT_VIDEO_DETAILS, videotuple)
                    if not success:
                        conn.rollback()
                        print("Failed to insert into DB")
                        return
        print("playlist data : ", playlisttuple)            
        if playlisttuple is not None:
            success = db.insertintoDB(conn, INSERT_PLAYLIST_DETAILS, playlisttuple)
            if not success:
                conn.rollback()
                print("Failed to insert into DB")
                return
    print("channel data : ", channeltuple)    
    if channeltuple is not None:
        success = db.insertintoDB(conn, INSERT_CHANNEL_DETAILS, channeltuple)
        if not success:
            conn.rollback()
            print("Failed to insert into DB")
            return
        
    conn.commit()
    return

def channelexistsindb(conn, channelid):
    query = "SELECT * FROM channel_details WHERE channel_id = %s"
    data = (channelid,)
    rows = db.selectfromDB(conn, query, data)
    if len(rows) == 0:
        return False
    else:
        return True

if __name__ == "__main__":
    main()
