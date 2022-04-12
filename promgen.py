import json
import openai
import random
from os import path
import argparse
import re
import os

api_key = os.environ.get("OPEN_AI_API")
openai.api_key = api_key 

my_engine = "ada"
#my_engine = "davinci"

styles_file = open( "prompgen_styles.txt", "r")
styles = styles_file.readlines()
styles_file.close()
artists_file = open( "prompgen_artists.txt", "r")
artists = artists_file.readlines()
artists_file.close()
keywords_file = open( "prompgen_keywords.txt", "r")
keywords = keywords_file.readlines()
keywords_file.close()
prompts_file = open( "prompgen_prompts.txt", "r")
pre_prompts = prompts_file.readlines()
prompts_file.close()
artist_intros = ["in the style of","by","inspired by","resembling"]

def get_args():
	user_input, batch_size = 'a boy', 25
	parser = argparse.ArgumentParser()
	parser.add_argument("prompt", help="the base prompt (comma seperate each weighted section")
	parser.add_argument("-b", "--batchsize", type = int, help="batch_size, the number of images")
	args = parser.parse_args()
	if args.batchsize:
		batch_size = args.batchsize	
	user_input = args.prompt
	return (user_input, batch_size)

def rand_item(my_list):
	intro = ''
	if my_list == artists:
		intro = 'by '
	return intro+random.choice(my_list).strip()

def rand_w():
	to_ret = str(random.randint(1,9))
	return (to_ret)

def get_result(user_prompt):
	prompt = """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ user_prompt
	response = openai.Completion.create(engine=my_engine, prompt=prompt, max_tokens=30, stop= "\n")
	result = response["choices"][0]["text"].strip()
	result = result.replace(',',(":"+rand_w()+'", "')).replace('.',(":"+rand_w()+'", "'))
	return result

def main():
	(user_input, batch_size) = get_args()
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
				prompt_to_append = prompt_to_append + rand_item(artists)
			elif section[0] == "^": #keyword is used
				prompt_to_append = prompt_to_append + rand_item(keywords)
			elif section[0] == ":":
				if section[-1] == ":": #if the char after the : is not a digit, then
					prompt_to_append = prompt_to_append + rand_item(random.choice([artists,styles,keywords]))+":"+rand_w()+'"'
			else:
				if ">" in section and section[0] != ">":
					user_prompt = section.split(">")[0]
					result = get_result(user_prompt, pre_prompts)
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

	for item in prompts:
		print("["+item.replace('""','"')+"],")

main()

