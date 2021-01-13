import pyaudio
#from tkinter import tkFileDialog
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def openSong(gui):
    if gui.song.wf:
        pauseStream(gui.song)
        gui.song.wf.close()
    fn = tk.filedialog.askopenfilename(initialdir="C\:",
                                       title="Select file to open",
                                       filetypes=(('.wav files','*.wav'),
                                                  ("all files","*.*")))
    [butt.config(state='normal') for butt in gui.allButts]
    gui.song.filepath = fn
    gui.song.openAudio()
    gui.song.loadAudioData()
    gui.song.refreshPlot()
    gui.canvas.draw()
    if gui.song.songname:
        t = gui.song.songname[0:-4]
    else:
        t = ''
    gui.songTitleL.config(text=t)

### button command functions
# open stream with pyaudio function
def openStream(song,rateFactor=1):
    song.stream = song.p.open(format=song.FORMAT,
                             channels=song.CHANNELS,
                             rate=int(song.RATE*rateFactor),
                             output=True,
                             stream_callback=lambda in_data,frame_count,time_info,status:callback(in_data,frame_count,time_info,status,song))
def playStream(song,rateFactor=1):
    if song.stream==None or not song.stream.is_active():
        openStream(song,rateFactor)
def stopStream(song):
    song.PLAYSEG = False
    if song.stream!=None and song.stream.is_active():
        song.stream.stop_stream()
        song.wf.rewind()
    elif song.stream==None:
        song.wf.rewind()
    else:
        song.wf.rewind()
def playPauseStream(song,rateFactor=1):
    if song.stream==None or not song.stream.is_active():
        openStream(song,rateFactor)
    elif song.stream.is_active():
        song.stream.stop_stream()
def pauseStream(song):
    if song.stream.is_active():
        song.stream.stop_stream()
def ffStream(song):
    pos = song.wf.tell()+song.RATE
    if pos >= song.NFrames:
        song.wf.setpos(song.NFrames-1)
    else:
        song.wf.setpos(song.wf.tell()+song.RATE)
def rwStream(song):
    pos = song.wf.tell()-song.RATE
    if pos<1:
        song.wf.setpos(1)
    else:
        song.wf.setpos(song.wf.tell()-song.RATE)
def playSeg(song):
    song.PLAYSEG = True
    #global slider
    song.wf.setpos(int(song.barL[0].xy[0]*song.RATE))
    playStream(song)
def repeatSeg(song,repeatSegB):
    song.REPEAT = not song.REPEAT
    if song.REPEAT:
        repeatSegB.config(relief='sunken')
    else:
        repeatSegB.config(relief='raised')

# pyaudio open stream uses this funtion to send data to the stream bit by bit
# so its a good place to add other mid-playback stuff like ff and rw
def callback(in_data,frame_count,time_info,status,song):
    data = song.wf.readframes(frame_count)
    if song.PLAYSEG:
        if song.wf.tell()>song.barR[0].xy[0]*song.RATE:
            if song.REPEAT:
                song.wf.setpos(int(song.barL[0].xy[0]*song.RATE))
            else:
                song.PLAYSEG = False
                return (data, pyaudio.paComplete)
    return (data, pyaudio.paContinue)
