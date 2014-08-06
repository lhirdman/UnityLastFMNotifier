#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import pynotify
import sys
import httplib2 as http
import json
import os
from datetime import datetime
import time
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

def send_message( title, message, image ):
    if not pynotify.init("Last.FM"):
        sys.exit(1)
    notice = pynotify.Notification(title, message, image)
    if not notice.show():
        print "Failed to send notification"
        sys.exit(1)
    return

def get_data( user ):
    headers = {
       'Accept': 'application/json',
       'Content-Type': 'application/json; charset=UTF-8'
    }
    api_key="ccfcd6b800861bf2057516f1bc09ebb2"
    lmethod="user.getrecenttracks"
    limit="5"
    uri="http://ws.audioscrobbler.com"
    path="/2.0/?method=" + lmethod + "&limit=" + limit + "&user=" + user + "&api_key=" + api_key + "&format=json"
    target = urlparse(uri+path)
    method='GET'
    body=''
    h = http.Http()
    response, content = h.request(
        target.geturl(),
        method,
        body,
        headers)
    if ( response.status==200 ):
      data = json.loads(content)
    else:
      print response.status
      data = { 'mystatus': response.status }
#    print uri + path
#    print json.dumps(content, sort_keys=True, indent=4, separators=(',', ': '))
#    print data['recenttracks']
    return data

def strip_it( data ):
    if ( data.has_key('recenttracks') ):
        mydata = data['recenttracks']
#        if ( mydata.has_key('track') ):
#            print "Track info found"
    else:
        print "Track info not found"
        return ( {'error': '1'} )
    data = data['recenttracks']['track'][0]
    track = data['name']
    artist = data['artist']['#text']
    image = data['image'][1]['#text']
#    playtime = datetime.strftime('',datetime.utcnow() - datetime.strptime(data['recenttracks']['track']['date']['#text'], '%d %b %Y, %H:%M')
#    print "The data:"
#    print data
    if ( data.has_key('date') ):
        playtime = data['date']['#text']
    else:
        playtime = time.asctime( time.localtime(time.time()) )
#    print "Playtime: " + playtime
    songid = data['mbid']
#    track = data['recenttracks']['track']['name']
#    artist = data['recenttracks']['track']['artist']['#text']
#    image = data['recenttracks']['track']['image'][1]['#text']
#    playtime = datetime.strftime('',datetime.utcnow() - datetime.strptime(data['recenttracks']['track']['date']['#text'], '%d %b %Y, %H:%M')
#    playtime = data['recenttracks']['track']['date']['#text']
#    songid = data['recenttracks']['track']['mbid']
#    print playtime
    mylist = {
        'track': track,
        'artist':  artist,
        'image': image,
        'pdate': playtime,
        'songid': songid
    }
    return mylist

def get_image( uri ):
   method = 'GET'
   h = http.Http()
   target = urlparse(uri)
   body = ''
   response, content = h.request(
        target.geturl(),
        method)
   #lmfile = open("cover.png", "wb")
   lmfile = open("/tmp/cover.png", "wb")
   lmfile.write(content);
   lmfile.close()
   #imgpath = "file://" + os.path.abspath(os.path.curdir) + "/cover.png"
   imgpath = "file:///tmp/cover.png"
   return imgpath

if len(sys.argv) == 1:
    print "usage: " + sys.argv[0] + " your_lastfm_username"
    sys.exit(1)

user = sys.argv[1]
oldTrackId = 'xxx'
oldTrackName = 'xxx'
oldImgPath = 'xxx'
while 1:
    data = get_data( user );
    if ( data.has_key('mystatus') ):
        continue

#    if ( len(data['recenttracks']['track']) == 2 ):
#        print "To much data overload: %d" % (len(data['recenttracks']['track']))
#        time.sleep(5)
#        continue
    mylist = strip_it( data );
    if ( mylist.has_key('error') ):
        print "Error occured: " + mylist['error']
        continue
    #print "Last knowned track id: " + oldTrackId
    if ( mylist['songid'] == '' ):
        if ( mylist['track'] == oldTrackName ):
#            print "No update available"
            time.sleep(5)
            continue
    elif ( mylist['songid'] == oldTrackId ):
#        print "No update available"
        time.sleep(5)
        continue

    print "New track id: " + mylist['songid']
    oldTrackId = mylist['songid']
    oldTrackName = mylist['track']
    #print mylist
    #track = mylist['track']
    #artist = mylist['artist'] 
    #image = mylist['image']
    #get_image( image );
    if ( mylist['image'] == oldImgPath ):
        print "No new image needed"
    else:
        if ( mylist['image'] != '' ):
            imgpath = get_image( mylist['image'] );
            oldImgPath = mylist['image']
        else:
            imgpath = 'dialog-question'
    #send_message( artist, track, imgpath );
    send_message( mylist['artist'], mylist['track'] + "\nPlayed on: " + mylist['pdate'], imgpath );
    #os.remove('cover.png')
    #send_message("Last.fm Now Playing","Some artist - A song");
    #print data['recenttracks']['track']
    time.sleep(5)
