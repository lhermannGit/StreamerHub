import threading
import queue
from livestreamer import Livestreamer, StreamError, PluginError, NoPluginError

class Executor(threading.Thread):
    
    def __init__(livestreamerPlayer, cmd_q): 
        this.livestreamerPlayer = livestreamerPlayer
        this.cmd_q = cmd_q
        this.livestreamer = Livestreamer()
        this.livestreamer.set_loglevel("info")
        this.livestreamer.set_logoutput(sys.stdout)

    def run():
        while True:
            (out_q, command) = cmd_q.get()
            execute(command, out_q)

    def execute(command, out_q):
        method = getattr(self, command[0], lambda: "nothing")

        return method(command, out_q)

    def Play(command, out_q):

        if len(command >= 2)
            url = command[1]
        else
            out_q.put("No URL provided for PLAY")

        # Attempt to fetch streams
        try:
            streams = this.livestreamer.streams(url)
        except NoPluginError:
            out_q.put("Livestreamer is unable to handle the URL '{0}'".format(url))
        except PluginError as err:
            out_q.put("Plugin error: {0}".format(err))

        if len(command) == 3
            quality = command[2]
        else
            quality = "best"

        stream = streams[quality]
        
        this.livestreamerPlayer.play(stream)

    def Pause(command, out_q):
        pass

    def Stop(command, out_q):
        this.livestreamerPlayer.stop()
