#!/usr/bin/env python
import threading
import Queue
import sys

from livestreamer import Livestreamer, StreamError, PluginError, NoPluginError
from LivestreamerPlayer import LivestreamerPlayer


class Executor(threading.Thread):
    
    def __init__(self, cmd_q): 
        self.livestreamerPlayer = LivestreamerPlayer()
        self.cmd_q = cmd_q
        self.livestreamer = Livestreamer()
        self.livestreamer.set_loglevel("info")
        self.livestreamer.set_logoutput(sys.stdout)

        threading.Thread.__init__ (self)

    def run(self):
        while True:
            (out_q, command) = self.cmd_q.get()
            execute(command, out_q)

    def execute(self, command, out_q):
        print "executing command " + command[0]
	    method = getattr(self, command[0], lambda: "nothing")

        return method(command, out_q)

    def Play(self, command, out_q):

        if len(command) >= 2:
            url = command[1]
        else:
            out_q.put("No URL provided for PLAY")

        # Attempt to fetch streams
        try:
            streams = self.livestreamer.streams(url)
        except NoPluginError:
            out_q.put("Livestreamer is unable to handle the URL '{0}'".format(url))
        except PluginError as err:
            out_q.put("Plugin error: {0}".format(err))

        if len(command) == 3:
            quality = command[2]
        else:
            quality = "best"

        stream = streams[quality]
        
        self.livestreamerPlayer.play(stream)

    def Pause(self, command, out_q):
        pass

    def Stop(self, command, out_q):
        self.livestreamerPlayer.stop()
