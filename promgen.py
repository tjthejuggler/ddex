import json
import openai
import random

from os import path

modifiers_file = open( "prompgen_modifiers.txt", "r")
modifiers = modifiers_file.readlines()
modifiers_file.close()

artists_file = open( "prompgen_artists.txt", "r")
artists = artists_file.readlines()
artists_file.close()

prompts_file = open( "prompgen_prompts.txt", "r")
pre_prompts = prompts_file.readlines()
prompts_file.close()

#@markdown Get your GPT-3 API key from https://openai.com

openai.api_key = "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" #@param {type:"string"}

phrase = "inside of a" #@param {type:"string"}
n = 30 #@param {type:"number"}

#@markdown _For collaboration and updates, email to martin.kallstrom@gmail.com_

using_weighted = True
prompts = []

def rand_w_item(my_list):
	intro = ''
	if my_list == artists:
		intro = ' by'
	return intro+random.choice(my_list).strip()+rand_w()

def construct_section(my_list):
	finished_section = ''
	if using_weighted:
		num_artists = random.randint(0,4)
		if num_artists == 1:
			finished_section = '"'+rand_w_item(my_list)+'",'
		if num_artists == 2:
			finished_section = '"'+rand_w_item(my_list)+'","'+rand_w_item(my_list)+'",'
		if num_artists == 3:
			finished_section = '"'+rand_w_item(my_list)+'","'+rand_w_item(my_list)+'","'+rand_w_item(my_list)+'",'
	#else:
	return finished_section

def rand_w():
	to_ret = ":"+str(random.randint(1,10))
	return (to_ret)

for j in range(n):
	prompt = ''
	if using_weighted:		
		prompt = """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """ + phrase 
	response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=30, stop= "\n")
	result = response["choices"][0]["text"].strip()
	artist_section = construct_section(artists)
	prompt_to_append = '["'+phrase + ' ' + result +'",' + artist_section + ',"trending on Artstation"]'
	if using_weighted:
		print('here')
		weighted_result = result.replace(',',(rand_w()+'","')).replace('.',(rand_w()+'","'))
		if weighted_result[-1] != '"':
			weighted_result = weighted_result + rand_w()+'",'
		prompt_to_append = '["'+phrase + ' ' + weighted_result + construct_section(artists) + construct_section(modifiers) + '"trending on Artstation'+rand_w()+'"]'
	prompts.append(prompt_to_append)

for item in prompts:
	print(item,",")

#todo
#get lots of great prompts
#eventually the artists can be put into categories