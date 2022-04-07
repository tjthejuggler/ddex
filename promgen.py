import json
import openai
import random
from os import path

phrase = "an art factory" #@param {type:"string"}
using_weighted = True
n = 40 #@param {type:"number"}

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


prompts = []

def rand_w_item(my_list):
	intro = ''
	if my_list == artists:
		intro = 'by '
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
		weighted_result = result.replace(',',(rand_w()+'","')).replace('.',(rand_w()+'","'))
		if weighted_result and weighted_result[-1] != '"':
			weighted_result = weighted_result + rand_w()+'",'
		prompt_to_append = '["'+phrase + ' ' + weighted_result + construct_section(artists) + construct_section(modifiers) + '"trending on Artstation'+rand_w()+'"]'
	prompts.append(prompt_to_append)

for item in prompts:
	print(item,",")

#todo
#if i ever get 2 ""s, then turn them into 1
#make a check for each finished line to see if iti is valid, if not then delete it?
#make it accept a full prompt and only alter the artists, styles, and weights
#	 (make arguments that make each of these choose randomly and then stay, or allow use to manually input any of the info
#		choose: prompts and/or prompt weights, and then same with artists and modifiers)
#get lots of great prompts
#eventually the artists can be put into categories
#	the ai could go out of its way to combine artists from various groups that should make interesting contrasts
#artstation variation
#	use deviantart
#	trending on
#	featured on
#artists into "in the style of"
#hook up arguments


#it could be set up to take an entire prompt and then give a bunch of variations on it

#@markdown _For collaboration and updates, email to martin.kallstrom@gmail.com_