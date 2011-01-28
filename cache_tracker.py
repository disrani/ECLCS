#!/usr/bin/python

import sys
import pyinotify
import optparse
import os
import re
from Tkinter import *
import thread

WHITE = '#ffffff'
GREEN = '#00ff00'
RED = '#ff0000'
BLUE = '#0000ff'

WIDTH = 200
HEIGHT = 800
BLOCK_WIDTH = 2
BLOCK_HEIGHT = 2

BLOCK_SIZE = 128 * 1024				# 128 KB
DISK_SIZE = 8 * 1024 * 1024 * 1024	# 8 GB
NUM_BLOCKS = DISK_SIZE / BLOCK_SIZE

write_pattern = re.compile(".* FUSE: Write (\d+) at (\d+)")
read_pattern = re.compile(".* FUSE: Read (\d+) at (\d+)")
reclaim_pattern = re.compile(".* FUSE: Reclaim: (\d+)")

last_pos = 0
img = None
canvas = None
block_status = dict() 

class NewLogDataHandler(pyinotify.ProcessEvent):
	def process_IN_MODIFY(self, event):
		global last_pos
		global img
		global block_status

		p,file_modified = os.path.split(event.pathname)
		if (fname == file_modified):
			f = open(options.log_file, 'r')
			# Go to the end of the log file
			f.seek(last_pos, os.SEEK_SET)
			lines = f.readlines()
			last_pos = f.tell()
			f.close()
			for l in lines:
				matches = write_pattern.findall(l)
				if (len(matches) > 0):
					length = int(matches[0][0])
					pos = int(matches[0][1])
					start,end = get_block_range(pos, length)
					while (start <= end):
						if (start in block_status and \
							block_status[start] != RED):
							update_block(start, BLUE)
						else: 
							update_block(start, GREEN)
						print start," in cache"
						start = start + 1
				else:
					matches = read_pattern.findall(l)
					if (len(matches) > 0):
						length = int(matches[0][0])
						pos = int(matches[0][1])
						start,end = get_block_range(pos, length)
						while (start <= end):
							if (start in block_status and \
								block_status[start] != RED):
								update_block(start, BLUE)
							else: 
								update_block(start, GREEN)
							print start," in cache"
							start = start + 1
					else: 
						matches = reclaim_pattern.findall(l)
						if (len(matches) > 0):
							pos = int(matches[0])
							update_block(pos, RED)
							print pos," removed from cache"
				
def update_block(num, color):
	global img
	global block_status

	block_status[num] = color
	col = num / WIDTH * BLOCK_WIDTH
	row = num % WIDTH * BLOCK_HEIGHT
	for i in range(col, col+BLOCK_WIDTH):
		for j in range(row, row+BLOCK_HEIGHT):
			img.put(color, (j,i))

def get_block_range(pos, length):
	start = pos / BLOCK_SIZE
	end = (pos + length) / BLOCK_SIZE
	return start,end

def read_from_log(notifier):
	lines = f.readlines()
	print lines

def start_ui():
	global img, canvas
	chunk_frames = []
	tk = Tk()
	tk.columnconfigure(0, weight=1)
	tk.rowconfigure(0, weight=1)

	mainFrame = Frame(tk)

	mainFrame['height'] = HEIGHT
	mainFrame['width'] = WIDTH

	img = PhotoImage(width = WIDTH, height = HEIGHT)
	img = PhotoImage(width=WIDTH, height=HEIGHT)

	for i in range(0,WIDTH):
		for j in range(0,HEIGHT):
			img.put(WHITE, (i,j))
			j += 1
		i += 1	
	canvas = Canvas(mainFrame, width=WIDTH, height=HEIGHT)
	canvas.pack()
	canvas.grid()
	canvas.create_image(0,0, image = img, anchor=NW)

	mainFrame.grid()
	thread.start_new_thread(tk.mainloop, ())

opts = optparse.OptionParser()
opts.add_option('--log_file', '-l', action='store')

options, args = opts.parse_args()

print "Num blocks:", NUM_BLOCKS

if (options.log_file is None):
	sys.exit("No log file name give")

f = open(options.log_file, 'r')
# Go to the end of the log file
f.seek(0, os.SEEK_END)
last_pos = f.tell()
f.close()

path,fname = os.path.split(options.log_file)
print "Path:", path
print "file:", fname

wm = pyinotify.WatchManager()
wm.add_watch(path, pyinotify.ALL_EVENTS, rec=True)

eh = NewLogDataHandler()
notifier = pyinotify.Notifier(wm, eh)
start_ui()
notifier.loop()

