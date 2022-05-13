#this program takes the text from each line in source.txt and prints TO TERMINAL(print) in the format shown in result.txt

import argparse #this is library that allows arguments to be passed in (python3 anim.py ARGUMENT(24))

#code for passing arguments when the program is run
parser = argparse.ArgumentParser()
parser.add_argument("fps", help="the frames multiplier for the given seconds")
args = parser.parse_args()

file = open( "source.txt", "r")
lines = file.readlines()

time = 0

for line in lines:
	seconds = int(line.split(' ')[0])
	frames = seconds * int(args.fps)
	print(str(frames) + ': [ " ' + line.split(' ',1)[1].strip() +' " ],')