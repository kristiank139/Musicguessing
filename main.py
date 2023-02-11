from tkinter import *
from tkinter import ttk
from pytube import Playlist
import vlc
import time
import pafy
import random
import os
import threading
import json
from tkinter.filedialog import askopenfilename
import pathlib
import platform
from threading import Thread

global files, i, guessed, link, guess, titleSet, randinteger
files = []
i = -1
guessed = False
names = {}
root = Tk()

if not os.path.exists(f"{os.getcwd()}/songs"):
    os.mkdir("songs")
else:
    for file in os.listdir(f"{os.getcwd()}/songs"):
        if file[-4:] != "tore":
            files.append(file)
            i += 1
    print(f"here{files}")

if not os.path.exists(f"{os.getcwd()}/names.json"):
    for i in range(len(files)):
        name = input(f"Enter the name for {files[i]}: ")
        names[files[i]] = name
    with open("names.json", "w",) as f:
        json.dump(names, f)
else:
    with open("names.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for key in data:
            names[key] = data[key]
        print(names)

randinteger = random.randint(0, i)
print(randinteger)
p = vlc.MediaPlayer()
class ttkTimer(Thread):
    """a class serving same function as wxTimer... but there may be better ways to do this
    """
    def __init__(self, callback, tick):
        Thread.__init__(self)
        self.callback = callback
        self.stopFlag = threading.Event()
        self.tick = tick
        self.iters = 0

    def run(self):
        while not self.stopFlag.wait(self.tick):
            self.iters += 1
            self.callback()

    def stop(self):
        self.stopFlag.set()

    def get(self):
        return self.iters

class Player(Frame):
    """The main window has to deal with events.
    """
    def __init__(self, parent, title=None):
        Frame.__init__(self, parent)

        self.parent = parent

        if title == None:
            title = "tk_vlc"
        self.parent.title(title)

        # The second panel holds controls
        self.videopanel = ttk.Frame(self.parent)
        self.canvas = Canvas(self.videopanel).pack(fill=BOTH,expand=1)
        self.videopanel.pack(fill=BOTH,expand=1)

        ctrlpanel = ttk.Frame(self.parent)
        pause  = ttk.Button(ctrlpanel, text="Pause", command=self.OnPause)
        play   = ttk.Button(ctrlpanel, text="Play", command=self.OnPlay)
        skip   = ttk.Button(ctrlpanel, text="Skip", command=self.OnSkip)

        pause.pack(side=LEFT)
        play.pack(side=LEFT)
        skip.pack(side=LEFT)
        self.volume_var = IntVar()
        self.volslider = Scale(ctrlpanel, variable=self.volume_var, command=self.volume_sel,
                from_=0, to=100, orient=HORIZONTAL, length=100)
        self.volslider.pack(side=LEFT, padx=20)
        self.volslider.set(62)
        ctrlpanel.pack(side=BOTTOM)

        ctrlpanel2 = ttk.Frame(self.parent)
        self.scale_var = DoubleVar()
        self.timeslider_last_val = ""
        self.timeslider = Scale(ctrlpanel2, variable=self.scale_var, command=self.scale_sel,
                from_=0, to=1000, orient=HORIZONTAL, length=500)
        self.timeslider.pack(side=BOTTOM, fill=X,expand=1)
        self.timeslider_last_update = time.time()
        ctrlpanel2.pack(side=BOTTOM,fill=X)


        # VLC player controls
        self.Instance = vlc.Instance()

        self.timer = ttkTimer(self.OnTimer, 1.0)
        self.timer.start()
        self.parent.update()    


    def OnExit(self, evt):
        """Closes the window.
        """
        self.Close()

    def OnPlay(self):
        """Toggle the status to Play/Pause.
        If no file is loaded, open the dialog window.
        """
        def sub_OnPlay(self=self):

            global i, p
            while len(files) > 0:
                print(len(files))
                global filename
                filename = files[randinteger].split(".")
                filename.pop(0)
                filename.pop(-1)
                # Playing the random song
                print(files[randinteger])
                p =     vlc.MediaPlayer(f"{os.getcwd()}/songs/{files[randinteger]}")
                p.audio_set_volume(62)
                p.play()

                # Waiting for it to start playing
                while MediaParsedChanged(p) == 0:
                    time.sleep(0.1)

                print(guessed)
                # Infinite loop that will break once guessed is equal to True
                while guessed == False:
                    pass

                print(files)
                files.remove(files[randinteger])
                print(files)
                i -= 1
                p.stop()
                time.sleep(1)
                setFalse(guessed)
            print(f"All songs played!")

            if platform.system() == 'Windows':
                p.set_hwnd(self.GetHandle())
            else:
                p.set_xwindow(self.GetHandle()) # this line messes up windows
        thread = threading.Thread(target=sub_OnPlay).start()
        print(thread)
        thread.start()


    def GetHandle(self):
        return self.videopanel.winfo_id()

    #def OnPause(self, evt):
    def OnPause(self):
        """Pause the player.
        """
        p.pause()

    def OnSkip(self):
        """Skip the player.
        """
        global guessed
        guessed = True
        time.sleep(0.05)
        guessed = False
        print("Here")

    def OnTimer(self):
        """Update the time slider according to the current movie time.
        """
        if p == None:
            return
        
        length = p.get_length()
        dbl = length * 0.001
        self.timeslider.config(to=dbl)

        tyme = p.get_time()
        if tyme == -1:
            tyme = 0
        dbl = tyme * 0.001
        self.timeslider_last_val = ("%.0f" % dbl) + ".0"
        if time.time() > (self.timeslider_last_update + 2.0):
            self.timeslider.set(dbl)

    def scale_sel(self, evt):
        if p == None:
            return
        nval = self.scale_var.get()
        sval = str(nval)
        if self.timeslider_last_val != sval:
            self.timeslider_last_update = time.time()
            mval = "%.0f" % (nval * 1000)
            p.set_time(int(mval)) # expects milliseconds


    def volume_sel(self, evt):
        if p == None:
            return
        volume = self.volume_var.get()
        if volume > 100:
            volume = 100
        if p.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")



    def OnToggleVolume(self, evt):
        """Mute/Unmute according to the audio button.
        """
        is_mute = p.audio_get_mute()

        p.audio_set_mute(not is_mute)
        self.volume_var.set(p.audio_get_volume())

    def OnSetVolume(self):
        """Set the volume according to the volume sider.
        """
        volume = self.volume_var.get()
        # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
        if volume > 100:
            volume = 100
        if p.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        pass
        #MessageBox.showerror(self, 'Error', errormessage)

def Tk_get_root():
    if not hasattr(Tk_get_root, "root"): #(1)
        Tk_get_root.root= Tk.Tk()  #initialization call is inside the function
    return Tk_get_root.root

def _quit():
    print("_quit: bye")
    root = Tk_get_root()
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    os._exit(1)


if not os.path.exists(f"{os.getcwd()}/songs"):
    os.mkdir("songs")
else:
    for file in os.listdir(f"{os.getcwd()}/songs"):
        if file[-4:] != "tore":
            files.append(file)
            i += 1

if not os.path.exists(f"{os.getcwd()}/names.json"):
    for i in range(len(files)):
        name = input(f"Enter the name for {files[i]}: ")
        names[files[i]] = name
    with open("names.json", "w",) as f:
        json.dump(names, f)
else:
    with open("names.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for key in data:
            names[key] = data[key]
        print(names)

player = Player(root, title="player")

# Checks if media is playing, if it is playing then returns 1, otherwise returns 0
def MediaParsedChanged(media):
    return media.is_playing()

# Downloading the songs from the playlist
def Download():
    if "playlist" in link.get() and link.get():
        p = Playlist(str(link.get()))
        if len(p.video_urls) == 0:
            print("Empty or private playlist, change playlist to public.")
        for url in p.video_urls:
            video = pafy.new(url)
            audio = video.audiostreams
            audio[3].download(filepath=f"{os.getcwd()}/songs")
    elif "youtube.com" in link.get():
        video = pafy.new(link.get())
        audio = video.audiostreams
        audio[3].download(filepath=f"{os.getcwd()}/songs")
    elif not link.get():
        print("Enter a link!")
    else:
        print("Not a Youtube link")


def setFalse(g):
    g = False

# Checks if the guess is correct
def guessChecker():


    global guessed
    setFalse(guessed)
    print(names[files[randinteger]])
    if guess.get().lower().strip() == names[files[randinteger]].lower().strip() and guess.get():
            guessed = True
            print("Correct")
    elif not guess.get():
        print("Enter a guess!")
    elif MediaParsedChanged(p) == 0:
        print("Song isn't playing yet!")
    else:
        print("Wrong guess")
    print(names[files[randinteger]].lower())
    time.sleep(0.9)
    guessed = False

def fileRename():
 # Renaming the file with the right format
    old_name = f"{os.getcwd()}/songs/{files[randinteger]}"
    replaced = f"{titleSet.get()}".replace(" ", "-").replace(":", "").replace(";", "")
    new_name = f"{os.getcwd()}/songs/.{replaced}.webm"
    os.rename(old_name, new_name)
    print(f"Filename set to .{replaced}.webm")

def skipSong():
    global guessed
    guessed = True
    time.sleep(0.05)
    guessed = False
    
# Tkinter
root.geometry("800x450")
root.resizable(1,1)
root.eval('tk::PlaceWindow . center')
root.title("Song guesser")

# Inputs
link = StringVar()
guess = StringVar()
titleSet = StringVar()

# Labels
Label(root, text="Enter song link or playlist: ").place(x=160, y=30)
Label(root, text="Guess the song author, type/genre and name(ex. creator Spiritus Gregoriuse koraal Veni): ").place(x=32, y=200)   

# Buttons
Button(root, text="Download", command=Download).place(x=595, y=58)
Button(root, text="Skip song", command=skipSong).place(x=230, y=135)
Button(root, text="Guess", command = guessChecker).place(x = 595, y = 239)

# Entries
linkEnter = Entry(root, width = 60, textvariable = link).place(x=25, y=60)
Entry(root, width = 60, textvariable = guess).place(x=25, y=240)

# Separator
ttk.Separator(root, orient='horizontal').place(x=0, y=100, width=800)
ttk.Separator(root, orient='horizontal').place(x=0, y=185, width=800)
ttk.Separator(root, orient='horizontal').place(x=0, y=285, width=800)


# On enter run the guessChecker function
root.bind('<Return>', lambda event: guessChecker())

root.mainloop()
