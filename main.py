from tkinter import *
from pytube import YouTube, Playlist
import vlc
import time
import pafy
import random
import os
import threading

root = Tk()

global files, i, guessed, link, guess, authorSet, genreSet, titleSet

files = []
i = -1
guessed = False

# Check if "songs" folder exists, if it doesn't, then creates it. Adds all the files in the folder to list "files"
if not os.path.exists(f"{os.getcwd()}/songs"):
    os.mkdir("songs")
else:
    for file in os.listdir(f"{os.getcwd()}/songs"):
        if file[-4:] != "tore":
            files.append(file)
            i += 1

# Checks if media is playing, if it is playing then returns 1, otherwise returns 0
def MediaParsedChanged(media):
    return media.is_playing()

# Downloading the songs from the playlist
def Download():
    if not os.path.exists(f"{os.getcwd()}/songs"):
        os.mkdir("songs")
    if "playlist" in link.get():
        p = Playlist(str(link.get()))
        if len(p.video_urls) == 0:
            print("Empty or private playlist, change playlist to public.")
        for url in p.video_urls:
            video = pafy.new(url)
            audio = video.audiostreams
            audio[3].download(filepath=f"{os.getcwd()}/songs")
    else:
        video = pafy.new(link.get())
        audio = video.audiostreams
        audio[3].download(filepath=f"{os.getcwd()}/songs")
    

    
# Plays a random song from the folder "songs" until there are no more songs to play
def Play():
    global i
    while len(files) > 0:
        global randinteger, filename
        randinteger = random.randint(0, i)
        filename = files[randinteger].split(".")
        filename.pop(0)
        filename.pop(-1)
        # Playing the random song
        p = vlc.MediaPlayer(f"{os.getcwd()}/songs/{files[randinteger]}")
        print(files[randinteger])
        p.audio_set_volume(62)
        p.play()

        # Waiting for it to start playing
        while MediaParsedChanged(p) == 0:
            time.sleep(0.1)

        # Infinite loop that will break once guessed is equal to True
        while guessed == False:
            pass

        files.remove(files[randinteger])
        i -= 1
        p.stop()
        time.sleep(1)
        setFalse(guessed)
    print(f"All {i} songs played")

def setFalse(g):
    g = False

# Checks if the guess is correct
def guessChecker():

    # Segregating the author, song name and genre
    for n in filename:
        if len(n.split("-")) > 1:
            split = n.split("-")
            filename[filename.index(n)] = " ".join(split)

    global guessed
    setFalse(guessed)
    print(filename)

    if guess.get().lower() == filename[0].lower() + " " + filename[1].lower() + " " + filename[2].lower():
            guessed = True
            print("Correct")
    time.sleep(0.9)
    guessed = False

def fileRename():
    # Renaming the file with the right format
    old_name = f"{os.getcwd()}/songs/{files[randinteger]}"
    replaced = f"{authorSet.get()}.{genreSet.get()}.{titleSet.get()}".replace(" ", "-").replace(":", " ").replace(";", "")
    new_name = f"{os.getcwd()}/songs/.{replaced}.webm"
    os.rename(old_name, new_name)
    print(f"Filename set to {replaced}")

def skipSong():
    global guessed
    guessed = True
    time.sleep(0.05)
    guessed = False
    
# Tkinter
root.geometry("800x550")
root.resizable(1,1)
root.eval('tk::PlaceWindow . center')
root.title("Song guesser")

# Inputs
link = StringVar()
guess = StringVar()
authorSet = StringVar()
genreSet = StringVar()
titleSet = StringVar()

# Labels
Label(root, text="Enter song link or playlist: ").place(x=160, y=30)
Label(root, text="Author: ").place(x=50, y=330)
Label(root, text="Genre: ").place(x=50, y=380)
Label(root, text="Title: ").place(x=50, y=430)
Label(root, text="Identify songs: ").place(x=50, y=290)
Label(root, text="Guess the song author, type/genre and name(ex. creator Spiritus Gregoriuse koraal Veni): ").place(x=32, y=200)   

# Buttons
Button(root, text="Download", command=Download).place(x=595, y=58)
Button(root, text="Rename file", command=fileRename).place(x=50, y=480)
play = Button(root, text="Play song", command=threading.Thread(target=Play).start).place(x=60, y=135)
Button(root, text="Skip song", command=skipSong).place(x=230, y=135)
Button(root, text="Guess", command = guessChecker).place(x = 595, y = 239)

# Entries
linkEnter = Entry(root, width = 60, textvariable = link).place(x=25, y=60)
authorEnter = Entry(root, width = 15, textvariable = authorSet).place(x=150, y=330)
genreEnter = Entry(root, width = 15, textvariable = genreSet).place(x=150, y=380)
titleEnter = Entry(root, width = 15, textvariable = titleSet).place(x=150, y=430)
Entry(root, width = 60, textvariable = guess).place(x=25, y=240)

root.mainloop()
