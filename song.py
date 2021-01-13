import os
import pydub
import pyaudio
import wave
import struct
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator,FuncFormatter
from matplotlib.lines import Line2D

class Song():
    def __init__(self,filepath=None,theSize=5,downsize=1000):
        # start variables
        self.filepath = filepath
        self.songname = None
        self.theSize = theSize
        self.downsize = downsize
        
        # audio
        self.p = pyaudio.PyAudio()
        self.wf = None
        self.stream = None
        self.FORMAT = None
        self.RATE = None
        self.NFrames = None
        self.duration = 150 # the blank song graph will be this long
        
        # the plot, empty song should be nice plot still
        self.data_L = [0,0]
        self.data_R = [0,0]
        self.data_T = [0,150]
        figL = 2*self.theSize
        figW = self.theSize/1.5
        self.fig,self.ax = plt.subplots(nrows=1,ncols=1,figsize=(figL,figW))
        self.curves = self.ax.plot(self.data_T,self.data_L,'r')
        self.ax.tick_params(labelsize=self.theSize*2,labelleft=False)
        self.ax.set_xlim([0,self.duration*1.1])
        self.ax.set_ylim([-1,1])
        self.ax.set_frame_on(False)
        self.ax.xaxis.set_ticks([0,30,60,90,120,150])
        self.ax.set_xticklabels(['00:00','00:30','01:00',
                                 '01:30','02:00','02:30'])
        self.fig.subplots_adjust(bottom=0.4)
        
        self.barL = self.ax.bar(0,1.5,bottom=-0.75,
                                width=0.94,color='k',zorder=10)
        self.barR = self.ax.bar(150,1.5,bottom=-0.75,
                                width=0.94,color='k',zorder=10)
        self.cursor = self.ax.bar(0,1.95,bottom=-0.75*1.3,
                                  width=0.31,color='k',zorder=10)
        self.lin = Line2D([0,150],[0,0],linewidth=self.theSize/2,
                          color='#00ffff',zorder=9)
        self.ax.add_line(self.lin)
        
        # other
        self.createdFilepaths = []
        self.press = None
        
        # flags
        self.PLAYSEG = False
        self.REPEAT = False
        self.ZOOM = 0
        
    # class attributes
    permittedIntervals = [0.0001,0.0002,0.0003,0.0005,0.001,0.002,
                          0.003,0.005,0.01,0.02,0.03,0.05,0.1,0.2,0.3,
                          0.5,1,2,3,5,10,15,30,60,120,180,300,600,900,
                          1800,3600,7200,14400,21600]    
    handledFormats = ['wav','m4a','mp3']
    
    def openAudio(self,convert_to_mono=False):
        self.songname = os.path.split(self.filepath)[1]
        filetype = self.songname.split('.')[1]
        playFilepath = self.filepath
        if filetype!='wav' and filetype in self.handledFormats:
            filename2 = self.songname.split('.')[0]+'.wav'
            filepath2 = os.path.split(self.filepath)[0]
            filepath2 = os.path.join(filepath2,filename2)
            song = pydub.AudioSegment.from_file(self.filepath,filetype)
            song.export(filepath2,format="wav")
            self.createdFilepaths.append(filepath2)
            playFilepath = filepath2
            del song
        elif filetype!='wav' and filetype not in self.handledFormats:
            raise Exception('Filetype {} unsupported.'.format(filetype))
        if convert_to_mono:
            filepath2 = playFilepath[0:-4]+'_mono.wav'
            song = pydub.AudioSegment.from_wav(playFilepath)
            song = song.set_channels(1)
            song.export(filepath2, format="wav")
            self.createdFilepaths.append(filepath2)
            playFilepath = filepath2
            del song

        self.wf = wave.open(playFilepath,'r')
        
        self.FORMAT = self.p.get_format_from_width(self.wf.getsampwidth())
        self.CHANNELS = self.wf.getnchannels()
        self.RATE = self.wf.getframerate()
        self.NFrames = self.wf.getnframes()
        self.duration = self.NFrames/self.RATE
    
    def loadAudioData(self):
        pos = self.wf.tell()
        self.wf.setpos(0)
        data = self.wf.readframes(self.NFrames)
        self.wf.setpos(pos)
        data = struct.unpack(str(self.NFrames*self.CHANNELS)+'h',data)
        self.data_L = data[::self.downsize*self.CHANNELS]
        self.data_T = [i/self.RATE for i in range(self.NFrames)]
        self.data_T = self.data_T[::self.downsize]
        del data
        
    def refreshPlot(self):
        # find x-axis interval
        D = self.duration/6
        ind = [(abs(D-d),i) for i,d in enumerate(self.permittedIntervals)]
        ind2 = sorted(ind)[0][1]
        interval = self.permittedIntervals[ind2]
        def timeformatter(x,pos):
            tick = str(int(x//60)).zfill(2)+':'+str(int(x%60)).zfill(2)
            return tick  
        
        
        for curve in self.curves:
            curve.remove()
        self.curves = self.ax.plot(self.data_T,self.data_L,'r')
        
        self.ax.xaxis.set_major_locator(MultipleLocator(base=interval))
        self.ax.xaxis.set_major_formatter(FuncFormatter(timeformatter))
        self.ax.autoscale(axis='y')
        
        # make slider and cursor
        xlim,ylim = self.ax.get_xlim(),self.ax.get_ylim()
        barheight = (ylim[1]-ylim[0])*0.75
        barbottom = -barheight/2
        barWidth = self.duration/160
        
        self.barL[0].set_x(0)
        self.barR[0].set_x(self.duration)
        self.cursor[0].set_x(0)
        self.barL[0].set_height(barheight)
        self.barR[0].set_height(barheight)
        self.cursor[0].set_height(barheight*1.3)
        self.barL[0].set_y(barbottom)
        self.barR[0].set_y(barbottom)
        self.cursor[0].set_y(barbottom*1.3)
        self.barL[0].set_width(barWidth)
        self.barR[0].set_width(barWidth)
        self.cursor[0].set_width(barWidth/3)
        
        self.lin.set_data([[0,self.duration],[0,0]])
        self.ax.set_xlim([0,self.duration*1.1])