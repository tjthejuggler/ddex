#this program takes the text from each line in source.txt and prints TO TERMINAL in the format shown in result.txt

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("frames", help="the number of frames between each prompt")
args = parser.parse_args()
print("THE FRAMES AGRUMENT PASSED BY THE USER IS: " + args.frames +"\n")

print("THE LINES IN SOURCE.TXT ARE: ")
file = open( "source.txt", "r")
lines = file.readlines()
for line in lines:
	print(line.strip())

