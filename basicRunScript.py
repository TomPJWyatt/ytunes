import tkinter as tk
import SongClass as song
import GUIClass as gui

root = tk.Tk()
s0 = song.Song()
g0 = gui.GUI(root,s0)
root.mainloop()