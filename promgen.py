import json
import openai
import random
from os import path
import argparse
import re
import os
import textwrap

api_key = os.environ.get("OPEN_AI_API")
openai.api_key = api_key 

engine = "ada"
engine = "davinci"

category_keys = {'2': 'religious', '3': 'hyperrealistic'}

def load_modifiers():
	styles_file = open( "prompgen_styles.txt", "r")
	styles = styles_file.readlines()
	styles_file.close()
	artists_file = open( "prompgen_artists.txt", "r")
	artists = artists_file.readlines()
	artists_file.close()

	artists_dict = {'bob' : ["religious", "hyperrealistic"], "charlie" : ["hyperrealistic", "happy"]}
	# if path.exists(cwd+'/promgen_artists_formatted.txt'):			
	# 	with open(cwd+'/promgen_artists_formatted.txt') as json_file:
	# 		artists_dict = json.load(json_file)

	keywords_file = open( "prompgen_keywords.txt", "r")
	keywords = keywords_file.readlines()
	keywords_file.close()
	prompts_file = open( "prompgen_prompts.txt", "r")
	pre_prompts = prompts_file.readlines()
	prompts_file.close()
	artist_intros = ["in the style of","by","inspired by","resembling"]

	return (styles, artists_dict, keywords, pre_prompts, artist_intros)

def get_args():
	user_input, batch_size = 'a boy', 25
	every_categories_filter, only_categories_filter = [], []
	parser = argparse.ArgumentParser(	    
		prog='PROG',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''\
			for use with -e and -a, comma seperated (ex: -e 1,5,14)
			Category Key:
			2 - religious
			3 - hyperrealistic

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

def rand_item(my_list):
	intro = ''
	if my_list == artists:
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
	cwd = os.getcwd()
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
	filtered_artists = artists_dict.keys()
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
	print('user_input', user_input)
	for i in range(batch_size):#this will run once for each prompt it will create
		prompt_to_append = ''
		for section in user_input.split(","): #analyze 
			section = section.replace('"', '')
			print('section', section)
			if len(prompt_to_append) > 1: #if we have already been through once, then make a ,
				prompt_to_append = prompt_to_append + ","
			prompt_to_append = prompt_to_append + '"'
			if section[0] == "$": #style is used
				prompt_to_append = prompt_to_append + rand_item(styles)
			elif section[0] == "@": #artist is used
				prompt_to_append = prompt_to_append + rand_item(filtered_artists)
			elif section[0] == "^": #keyword is used
				prompt_to_append = prompt_to_append + rand_item(keywords)
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
						prompt_to_append = user_input
			if section[0] == "$" or section[0] == "@" or section[0] == "^":
				if len(section) > 1:
					if section[1] == ":" and section[-1] == ":": #if no weight is given, then use a random weight
						prompt_to_append = prompt_to_append + ":"+rand_w()
					else:
						prompt_to_append = prompt_to_append + user_input.split(":")[1]
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

