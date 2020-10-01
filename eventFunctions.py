from matplotlib.ticker import MultipleLocator

# this just stores some data if the click is on the slider
def on_press(event,song,CLICKMODE):
    # ignore if not in axes
    if event.inaxes != song.ax: 
        return
    # find if one of the bars was clicked
    containsL,attrdL = song.barL[0].contains(event)
    containsR,attrdR = song.barR[0].contains(event)
    # get coords of clicked bar
    if CLICKMODE.get()=='slide' and containsL: 
        x0, y0 = song.barL[0].xy
        barN = 0
        song.press = x0,y0,event.xdata,event.ydata,barN
    elif CLICKMODE.get()=='slide' and containsR:
        x0, y0 = song.barR[0].xy
        barN = 1
        song.press = x0,y0,event.xdata,event.ydata,barN
    elif CLICKMODE.get()=='curse':
        song.wf.setpos(int(event.xdata*song.RATE))
    elif CLICKMODE.get()=='mag+':
        zoomIn(event.xdata,song)
    elif CLICKMODE.get()=='mag-':
        zoomOut(event.xdata,song)
    else:
        return
    
# this is what does the moving
def on_motion(event,song):
    # ignore if not during click and in axis:
    if song.press is None: 
        return
    if event.inaxes != song.ax: 
        return
    # now do the shift just in x
    x0,y0,xpress,ypress,barN = song.press
    dx = event.xdata - xpress
    # this changes 1 -> 0 and 0 -> 1
    barN2 = abs(barN-1)
    bars = [song.barL,song.barR]
    bars[barN][0].set_x(x0+dx)
    if song.barR[0].xy[0] - song.barL[0].xy[0] < 0:
        bars[barN][0].set_x(bars[barN2][0].xy[0])
    #song.lin.set_data([[song.barL[0].xy[0]+(song.theSize*2**-song.ZOOM)-3*2**(-song.ZOOM-1),song.barR[0].xy[0]],[0,0]])
    song.lin.set_data([[song.barL[0].xy[0]+song.barL[0].get_width(),song.barR[0].xy[0]],[0,0]])
    song.fig.canvas.draw()

# just reset
def on_release(event,song):
    song.press = None
    song.fig.canvas.draw()    
    
def zoomIn(xpos,song):
    song.ZOOM += 1
    xlim = song.ax.get_xlim()
    xRadN = (xlim[1] - xlim[0])/4
    if xpos-xRadN < 0:
        x0N = 0
        xfN = 2*xRadN
    elif xpos+xRadN > song.duration:
        x0N = song.duration - 2*xRadN
        xfN = song.duration
    else:
        x0N = xpos - xRadN
        xfN = xpos + xRadN
    
    song.ax.set_xlim([x0N,xfN])
    ind = sorted([(abs((xfN-x0N)/6-d),i) for i,d in 
                  enumerate(song.permittedIntervals)])[0][1]
    interval = song.permittedIntervals[ind]
    song.ax.xaxis.set_major_locator(MultipleLocator(base=interval))
    
    song.cursor[0].set_width(song.cursor[0].get_width()/2)
    song.barL[0].set_width(song.barL[0].get_width()/2)
    song.barR[0].set_width(song.barR[0].get_width()/2)
    #song.lin.set_data([[song.barL[0].xy[0]+song.theSize*2**-song.ZOOM-3*2**(-song.ZOOM-1),song.barR[0].xy[0]],[0,0]])
    song.lin.set_data([[song.barL[0].xy[0]+song.barL[0].get_width(),song.barR[0].xy[0]],[0,0]])
    
def zoomOut(xpos,song):
    song.ZOOM -= 1
    xlim = song.ax.get_xlim()
    xRadN = (xlim[1] - xlim[0])
    if xpos-xRadN < 0:
        x0N = 0
        xfN = 2*xRadN
    elif xpos+xRadN > song.duration:
        x0N = song.duration - 2*xRadN
        xfN = song.duration
    else:
        x0N = xpos - xRadN
        xfN = xpos + xRadN
    
    song.ax.set_xlim(x0N,xfN)
    ind = sorted([(abs((xfN-x0N)/6-d),i) for i,d in 
                  enumerate(song.permittedIntervals)])[0][1]
    interval = song.permittedIntervals[ind]
    song.ax.xaxis.set_major_locator(MultipleLocator(base=interval))
    
    song.cursor[0].set_width(song.cursor[0].get_width()*2)
    song.barL[0].set_width(song.barL[0].get_width()*2)
    song.barR[0].set_width(song.barR[0].get_width()*2)
    #song.lin.set_data([[song.barL[0].xy[0]+song.theSize*2**-song.ZOOM-3*2**(-song.ZOOM-1),song.barR[0].xy[0]],[0,0]])
    song.lin.set_data([[song.barL[0].xy[0]+song.barL[0].get_width(),song.barR[0].xy[0]],[0,0]])
    
def updateCursor(gui):
    if gui.song.wf:
        pos = gui.song.wf.tell()/gui.song.RATE
        gui.song.cursor[0].set_x(pos)
        gui.canvas.draw()
    gui.root.after(250,gui.updateCursor)  