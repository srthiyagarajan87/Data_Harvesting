import configparser
import streamlit as st
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
import numpy as np

import channeldetails as ytapi
import DBConnect as db
import globals as g

st.title("YouTube Data Harvesting")
def main():
    
    channelid = st.text_input("Channel Id : ", "", max_chars=50, )
    subbutton = st.button("Fetch Channel Details")

    init()
   
    if subbutton:
        fetchchanneldetails(channelid)

def fetchchanneldetails(channelid):

    print("inside fetchchanneldetails ********** channelid : ", channelid)
    print("connection id : ", g.conn)

    if channelid == "":
        st.write("Please enter a valid Channel Id")
        return
    
    channelDict = ytapi.channeldetails(g.conn, g.youtube, channelid)
    if channelDict is not None:
        st.rerun()
    else:
        st.write("No channel details found")
        return

def displaychanneldetails():
    if len(ytapi.channelList) > 0:
        g.channeldf = pd.DataFrame(ytapi.channelList)
        g.channeldf.index = range(1, 1 + len(g.channeldf))

        st.dataframe(g.channeldf, on_select="rerun", key='channeldf', selection_mode='single-row')

        savebutton = st.button("Save All")
        if savebutton:
            savechannelstodb()

def savechannelstodb():
    st.write("Saving channels to DB")
    ytapi.saveallchannels(g.conn)


def on_cell_select():
    #st.write(st.session_state.channeldf["selection"]["rows"][0])
    index = st.session_state.channeldf["selection"]["rows"][0]
    g.selectedchannelid = ytapi.getchannelid(index)
    st.write(g.selectedchannelid)
    #displaychannelinfo(selectedchannelid)
    

def displaychannelinfo():

    print ("inside displaychannelinfo ********** channelid : ", g.selectedchannelid)  
    if g.selectedchannelid is not None:
        playlist =ytapi.getplaylist(g.selectedchannelid)
        if playlist is None:
            st.write("No playlist details found for the selected channel ", g.selectedchannelid)
            return
        
        videolist = ytapi.getvideo(playlist)
        if videolist is None:
            st.write("No video details found for the selected channel ", g.selectedchannelid)
            return
        
        commentlist = ytapi.getcomment(videolist)
        if commentlist is None:
            st.write("No comment details found for the selected channel ", g.selectedchannelid)
            return
        
        st.write("PlayList :")
        g.playlistdf = pd.DataFrame(playlist)
        g.playlistdf.index = range(1, 1 + len(g.playlistdf))
        st.dataframe(g.playlistdf)

        st.write("Video List : ")
        g.videodf = pd.DataFrame(videolist)
        g.videodf.index = range(1, 1 + len(g.videodf))
        st.dataframe(g.videodf)

        st.write("Comment List : ")
        g.commentdf = pd.DataFrame(commentlist)
        g.commentdf.index = range(1, 1 + len(g.commentdf))
        st.dataframe(g.commentdf)

        dummycol, delcol, savecol = st.columns([7, 1.5, 1.5])

        with savecol:
            savechannelbutton = st.button("Save This Channel")
            if savechannelbutton:
                saveselectedchannelstodb()
                

        with delcol:
            deletechannelbutton = st.button("Clear This Channel")
            if deletechannelbutton:
                deletechannelfromdb()

def saveselectedchannelstodb():

    if g.channeldf is None or g.playlistdf is None or g.videodf is None or g.commentdf is None:
        st.write("Some channel details are missing. Couldn't save this channel")
        return
   
    
    print ("Saving this channel")
    chnsave = ytapi.savethischannel(g.conn, g.selectedchannelid, g.channeldf, g.playlistdf, g.videodf, g.commentdf) 
    if not chnsave:
        print("Failed to insert into DB")
        return  
    ytapi.deletechannel(g.selectedchannelid)
    st.rerun()
    #st.write("Saving selected channel to DB")
    

def deletechannelfromdb():
    #st.write("Deleting selected channel from DB")
    ytapi.deletechannel(g.selectedchannelid)
    st.rerun()
    #displaychanneldetails()

def init():
    
    displaychanneldetails()
    
    if "channeldf" in st.session_state and len(st.session_state.channeldf["selection"]["rows"]) > 0:
        print(st.session_state.channeldf)
        index = st.session_state.channeldf["selection"]["rows"][0]
        g.selectedchannelid = ytapi.getchannelid(index)
        print("selectedchannelid: ", g.selectedchannelid)
        if g.selectedchannelid is not None:
            st.write(g.selectedchannelid)
            displaychannelinfo()

#if __name__ == "__main__":
main() 