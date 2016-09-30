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
	self.livestreamer.set_option("http-headers", "Client-ID=jzkbprff40iqj646a697cyrvl0zt2m6")
        threading.Thread.__init__ (self)

    def run(self):
        while True:
            (out_q, command) = self.cmd_q.get()
            print command
            self.execute(command, out_q)

    def execute(self, command, out_q):
        method = getattr(self, command['command'], lambda: "nothing")
	print command['command']
        return method(command, out_q)

    def Play(self, command, out_q):

        if not 'url' in command:
           out_q.put("No URL provided to play")
        else:
            # Attempt to fetch streams
            try:
                print "[Debug] URL to play '{0}'".format(command['url'])
		streams = self.livestreamer.streams(command['url'])
            except NoPluginError:
                out_q.put("Livestreamer is unable to handle the URL '{0}'".format(command['url']))
            except PluginError as err:
                out_q.put("Plugin error: {0}".format(err))

            if 'quality' in command:
                quality = command['quality']
            else:
                quality = 'medium'

            stream = streams[quality]

            self.livestreamerPlayer.play(stream)

            out_q.put("started streaming '{0}' ".format(command['url']))

    def Pause(self, command, out_q):
        pass

    def Stop(self, command, out_q):
        self.livestreamerPlayer.stop()
