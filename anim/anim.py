#this program takes the text from each line in source.txt and prints TO TERMINAL(print) in the format shown in result.txt

import argparse #this is library that allows arguments to be passed in (python3 anim.py ARGUMENT(24))



#code for passing arguments when the program is run
parser = argparse.ArgumentParser()
parser.add_argument("frames", help="the  number of frames between each prompt")
args = parser.parse_args()

file = open( "source.txt", "r")
lines = file.readlines()

time = 0

for line in lines:
	print('"'+ str(time) + '":[ " ' + line.strip() +' " ]')
	time=time+int(args.frames)



