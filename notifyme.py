#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pynotify
title = "Last.FM - Now Playing"
message = "Some Artist - Some song"
def sendmessage(title, message):
    pynotify.init("Test")
    notice = pynotify.Notification(title, message)
    notice.show()
    return
