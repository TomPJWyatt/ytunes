import tkinter as tk
import song
import gui

root = tk.Tk()
s0 = song.Song()
g0 = gui.GUI(root,s0)
root.mainloop()
