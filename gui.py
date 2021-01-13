import os
from tkinter import Menu, PhotoImage, Button, StringVar, Radiobutton, Label
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import buttonFunctions as b
import eventFunctions as e

class GUI():
    def __init__(self,root,song):
        # given parameters
        self.root = root
        self.song = song

        # main window
        self.root.title("Song segment player")
        self.root.iconbitmap(r'Images/icon.ico')
        self.root.configure(background='white')

        # menubar
        self.menubar = Menu(self.root)
        self.filemenu = Menu(self.menubar,tearoff=0)
        self.filemenu.add_command(label="Open",
                                  command=lambda:b.openSong(self))
        self.menubar.add_cascade(label="File",menu=self.filemenu)

        # images for buttons
        self.segmentIm = PhotoImage(file=r'Images/SegmentB.png')
        self.repSegIm = PhotoImage(file=r'Images/Repeat.png')
        self.playIm = PhotoImage(file=r'Images/PlayB.png')
        self.pauseIm = PhotoImage(file=r'Images/PauseB.png')
        self.stopIm = PhotoImage(file=r'Images/StopB.png')
        self.ffIm = PhotoImage(file=r'Images/ffB.png')
        self.rwIm = PhotoImage(file=r'Images/rwB.png')
        self.fullSpeedIm = PhotoImage(file=r'Images/FullSpeedB.png')
        self.halfSpeedIm = PhotoImage(file=r'Images/HalfSpeedB.png')
        self.sliderIm = PhotoImage(file=r'Images/SliderB.png')
        self.cursorIm = PhotoImage(file=r'Images/Cursor.png')
        self.magPlusIm = PhotoImage(file=r'Images/MagPlus.png')
        self.magMinusIm = PhotoImage(file=r'Images/MagMinus.png')

        # making buttons
        self.segmentB = Button(image=self.segmentIm,
                               command=lambda:b.playSeg(self.song))
        self.repSegB = Button(image=self.repSegIm,
                                 command=lambda:b.repeatSeg(self.song,self.repSegB))
        self.playB = Button(image=self.playIm,
                            command=lambda:b.playStream(self.song))
        self.pauseB = Button(image=self.pauseIm,
                             command=lambda:b.pauseStream(self.song))
        self.stopB = Button(image=self.stopIm,
                            command=lambda:b.stopStream(self.song))
        self.ffB = Button(image=self.ffIm,
                          command=lambda:b.ffStream(self.song))
        self.rwB = Button(image=self.rwIm,
                          command=lambda:b.rwStream(self.song))
        self.fullSpeedB = Button(image=self.fullSpeedIm)
        self.halfSpeedB = Button(image=self.halfSpeedIm)
        # making radio buttons
        self.CLICKMODE = StringVar(value="slide")
        self.sliderB = Radiobutton(
            self.root,
            image=self.sliderIm,
            variable=self.CLICKMODE,
            value='slide',
            indicatoron=0)
        self.cursorB = Radiobutton(
            self.root,
            image=self.cursorIm,
            variable=self.CLICKMODE,
            value='curse',
            indicatoron=0)
        self.magPlusB = Radiobutton(
            self.root,
            image=self.magPlusIm,
            variable=self.CLICKMODE,
            value='mag+',
            indicatoron=0)
        self.magMinusB = Radiobutton(
            self.root,
            image=self.magMinusIm,
            variable=self.CLICKMODE,
            value='mag-',
            indicatoron=0)

        # setting button parameters
        self.allButts = [self.segmentB,self.repSegB,self.playB,self.stopB,
                         self.pauseB,self.ffB,self.rwB,self.fullSpeedB,
                         self.halfSpeedB,self.sliderB,self.cursorB,
                         self.magPlusB,self.magMinusB]
        [butt.config(bg='white') for butt in self.allButts]
        # disable all buttons to start with
        [butt.config(state='disabled') for butt in self.allButts]
        self.sliderB.config(state='normal')

        # placing buttons
        rowc = 3
        self.segmentB.grid(row=0,column=2)
        self.repSegB.grid(row=0,column=3)
        self.playB.grid(row=rowc,column=3)
        self.pauseB.grid(row=rowc,column=2)
        self.stopB.grid(row=rowc,column=1)
        self.ffB.grid(row=rowc,column=4)
        self.rwB.grid(row=rowc,column=0)
        self.fullSpeedB.grid(row=0,column=4,columnspan=3)
        self.halfSpeedB.grid(row=0,column=5,columnspan=3)
        self.sliderB.grid(row=2,column=0)
        self.cursorB.grid(row=2,column=1)
        self.magPlusB.grid(row=2,column=2)
        self.magMinusB.grid(row=2,column=3)

        # display song title
        if self.song.songname:
            t = self.song.songname[0:-4]
        else:
            t = ''
        self.songTitleL = Label(self.root,text=t,bg='white')
        self.songTitleL.grid(row=0,column=0)

        # making figure canvas
        self.canvas = FigureCanvasTkAgg(self.song.fig,master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=rowc-2,column=0,columnspan=5)

        # connecting canvas to monitor events
        self.cidpress = self.canvas.mpl_connect(
            'button_press_event',
            lambda event:e.on_press(event,self.song,self.CLICKMODE))
        self.cidrelease = self.canvas.mpl_connect(
            'button_release_event',
            lambda event:e.on_release(event,self.song))
        self.cidmotion = self.canvas.mpl_connect(
            'motion_notify_event',
            lambda event:e.on_motion(event,self.song))

        self.root.bind('<space>', lambda event:b.playPauseStream(self.song))
        self.root.bind('<Return>', lambda event:b.playSeg(self.song))

        # set cursor updating
        self.root.after(10000,lambda: e.updateCursor(self))

        # insert menu bar
        self.root.config(menu=self.menubar)

        # closing behaviour
        self.root.protocol("WM_DELETE_WINDOW",self.on_closing)



    def on_closing(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.canvas.mpl_disconnect(self.cidrelease)
        self.canvas.mpl_disconnect(self.cidmotion)
        self.root.destroy()
        self.song.wf.close()
        self.song.stream.close()
        self.song.p.terminate()
        [os.remove(s) for s in self.song.createdFilepaths]

    def updateCursor(self):
        if self.song.wf:
            pos = self.song.wf.tell()/self.song.RATE
            self.song.cursor[0].set_x(pos)
            self.canvas.draw()
        self.root.after(250,self.updateCursor)
