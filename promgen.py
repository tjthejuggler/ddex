import json
import openai
import random
from os import path
import argparse
import re
import os
import textwrap

# DD
# ["hatice is a very attractive person and very sociable:3", "if you are interested go for it:3", "who knows?:9"], 
# ["hatice is a very sweet girl:7", "dress and caresses like dolls:7", "always returns a sign:2"]

# CD

#              first image              second image
# DD format - ["cat","yellow and red"],["dog","green"]

#               first image            second image
# CD format - ["cat, yellow and red", "dog, green"]

#bugs
#"a big dog:9,@:3"
#["a big dog:9","by Diego Velázquez9,@"],
#["a big dog:9","by Diego Velázquez:3"],

#"hatice is a very,@"
#[hatice is a very,@,"by Adam Paquette"],
#["hatice is a very","by Adam Paquette"],


cwd = os.getcwd() #

use_CD_format = True

api_key = os.environ.get("OPEN_AI_API")
openai.api_key = api_key 

engine = "ada"
engine = "davinci"

category_keys = {
			'2': 'religious', '3': 'hyperrealistic', '4': 'realistic', '5': 'surreal',
			'6': 'abstract', '7': 'fantasy', '8': 'cute', '9': 'people', '10': 'creatures', '11': 'nature',
			'12': 'buildings', '13': 'space', '14': 'objects', '15': 'boats', '16': 'cars',
			'17': 'pencil',	'18': 'paint', '19': 'CGI', '20': 'colorful', '21': 'dull', '22': 'black and white',
			'26': 'new','27': 'old','28': 'creepy',	'29': 'cartoon'
			}

def load_modifiers():
	styles_file = open( "prompgen_styles.txt", "r")
	styles = styles_file.readlines()
	styles_file.close()
	artists_file = open( "prompgen_artists.txt", "r")
	artists = artists_file.readlines()
	artists_file.close()
	artists_dict = {}
	#artists_dict = {'bob' : ["religious", "hyperrealistic"], "charlie" : ["hyperrealistic", "happy"]}
	if path.exists('./promgen_artists_formatted.txt'):	
		print('file exists')		
		with open('./promgen_artists_formatted.txt') as json_file:
			artists_dict = json.load(json_file)
	keywords_file = open( "prompgen_keywords.txt", "r")
	keywords = keywords_file.readlines()
	keywords_file.close()
	prompts_file = open( "prompgen_prompts.txt", "r")
	pre_prompts = prompts_file.readlines()
	prompts_file.close()
	artist_intros = ["in the style of","by","inspired by","resembling"]

	return (styles, artists_dict, keywords, pre_prompts, artist_intros)

def get_args():
	user_input, batch_size = 'a boy', 2
	every_categories_filter, only_categories_filter = [], []
	parser = argparse.ArgumentParser(	    
		prog='PROG',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''\
			for use with -e and -a, comma seperated (ex: -e 1,5,14)
			Category Key:
			2 religious 
			3 hyperrealistic (very close to photos) - this one may be rare
			4 realistic (actual real things, but obviously not a photo)
			5 surreal (breaks usual physics)
			6 abstract (lots of shapes and patterns, not everything is identifiable)
			7 fantasy (witches, angels, magic, dragons, faries..)
			8 cute
			9 people
			10 creatures (real or unreal animals)
			11 nature
			12 buildings
			13 space
			14 objects
			15 boats 
			16 cars
			17 pencil
			18 paint
			19 CGI
			20 colorful
			21 dull (not bright colors)
			22 black and white
			26 new
			27 old
			28 creepy (scary evil scary big animals)
			29 cartoon

			'''))
	parser.add_argument("prompt", help="the base prompt (comma seperate each weighted section")
	parser.add_argument("-b", "--batchsize", type = int, help="batch_size, the number of images")
	parser.add_argument("-e", "--everycat", type = str, help="use every modifier in these categories")
	parser.add_argument("-o", "--onlycat", type = str, help="use only modifiers that have all these categories")

	args = parser.parse_args()
	if args.batchsize:
		batch_size = args.batchsize	
	if args.everycat:
		every_categories_filter = [x for x in args.everycat.split(",")]
	if args.onlycat:
		only_categories_filter = [x for x in args.onlycat.split(",")]
	user_input = args.prompt
	return (user_input, batch_size, every_categories_filter, only_categories_filter)

def rand_item(my_list, is_artist):
	intro = ''
	if is_artist:
		intro = 'by '
	return intro+random.choice(my_list).strip()

def rand_w():
	to_ret = str(random.randint(1,9))
	return (to_ret)

def get_gpt_result(user_prompt, pre_prompts):
	prompt = """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ user_prompt
	response = openai.Completion.create(engine=engine, prompt=prompt, max_tokens=30, stop= "\n")
	result = response["choices"][0]["text"].strip()
	result = result.replace(',',(":"+rand_w()+'", "')).replace('.',(":"+rand_w()+'", "'))
	return result

def create_output_file(filename, output_lines):
	#print('creating output file', filename)
	
	folder_name = engine
	with open(cwd+'/'+folder_name+'/'+filename + '.txt', 'w') as f:
		for item in output_lines:
			f.write("[%s]\n" % item.strip("\n"))

def get_every_filter(artists_dict, filter_list):
	listOfKeys = list()
	listOfItems = artists_dict.items()
	for filter_key in filter_list:
		filter_word = category_keys[filter_key]
		for artist in artists_dict.keys():
			if filter_word in artists_dict[artist] and artist not in listOfKeys:
				listOfKeys.append(artist)
	return listOfKeys

def get_only_filter(artists_dict, filter_list):
	listOfKeys = list()
	listOfItems = artists_dict.items()
	for artist in artists_dict.keys():
		should_append = True
		for filter_key in filter_list: 
			filter_word = category_keys[filter_key]
			if not (filter_word in artists_dict[artist] and artist not in listOfKeys):
				should_append = False
		if should_append:
			listOfKeys.append(artist)
	return listOfKeys

def main():
	user_input, batch_size, every_categories_filter, only_categories_filter = get_args()
	styles_file = open( "prompgen_styles.txt", "r")
	styles, artists_dict, keywords, pre_prompts, artist_intros = load_modifiers()
	artist_intros = ["in the style of","by","inspired by","resembling"]
	filtered_artists = list(artists_dict.keys())
	print('fa',filtered_artists)
	print(["house", "car"])
	if every_categories_filter and only_categories_filter:
		print("You can't use 'every' filter and 'only' filter together")
		quit()
	elif every_categories_filter:
		filtered_artists = get_every_filter(artists_dict, every_categories_filter)
		print(filtered_artists)
	elif only_categories_filter:
		filtered_artists = get_only_filter(artists_dict, only_categories_filter)
		print(filtered_artists)
	user_prompt = ''	
	prompts = []
	print('user_input', user_input) #a big dog,@
	for i in range(batch_size):#this will run once for each prompt it will create
		prompt_to_append = ''
		for section in user_input.split(","): #analyze 
			section = section.replace('"', '')
			print('section', section) # a big red dog  -------------- @

			if len(prompt_to_append) > 1: #if we have already been through once, then make a ,
				prompt_to_append = prompt_to_append + ","
			prompt_to_append = prompt_to_append + '"'
			if section[0] == "$": #style is used
				prompt_to_append = prompt_to_append + rand_item(styles, False)
			elif section[0] == "@": #artist is used
				prompt_to_append = prompt_to_append + rand_item(filtered_artists, True)
			elif section[0] == "^": #keyword is used
				prompt_to_append = prompt_to_append + rand_item(keywords, False)
			elif section[0] == ":":
				if section[-1] == ":": #if the char after the : is not a digit, then
					prompt_to_append = prompt_to_append + rand_item(random.choice([artists,styles,keywords]))+":"+rand_w()+'"'
			else:
				if ">" in section and section[0] != ">":
					user_prompt = section.split(">")[0]
					result = get_gpt_result(user_prompt, pre_prompts)
					prompt_to_append = prompt_to_append + user_prompt+' '+result
					if section[-1] == ":":
						prompt_to_append = prompt_to_append + ":"+rand_w()
					prompt_to_append = prompt_to_append + ":"+rand_w()+'"'
				else:
					if ":" in section:
						prompt_to_append = prompt_to_append + section+'"'
						if section[-1] == ":":
							prompt_to_append = prompt_to_append + rand_w()+'"'
					else:
						prompt_to_append = '"'+ section + '"'
			if section[0] == "$" or section[0] == "@" or section[0] == "^":
				if len(section) > 1: #    @:4  
					if section[1] == ":" and section[-1] == ":": #if no weight is given, then use a random weight
						prompt_to_append = prompt_to_append + ":"+rand_w()
					else:
						prompt_to_append = prompt_to_append + ":" + section.split(":")[1]
				prompt_to_append = prompt_to_append + '"'
		print('prompt_to_append', prompt_to_append)
		prompt_to_append = prompt_to_append.replace('""', '"').replace('" ', '"')
		prompt_to_append = re.sub(' +', ' ', prompt_to_append).replace(" ,]", "]")
		prompt_to_append = re.sub('":\d+','', prompt_to_append)
		prompt_to_append = re.sub('", :\d+','", ', prompt_to_append)
		prompt_to_append = prompt_to_append.replace('", ","', ", ")
		#:5:8
		prompt_to_append = re.sub(':\d:\d',':'+rand_w(), prompt_to_append)
		prompt_to_append = prompt_to_append.replace('", ", ', '')
		prompt_to_append = prompt_to_append.replace(':"', ':')
		prompts.append(prompt_to_append)
	create_output_file(user_prompt.replace(' ', '_')+str(random.randint(0,1000000)), prompts)
	for item in prompts:
		print("["+item.replace('""','"')+"],")

main()

