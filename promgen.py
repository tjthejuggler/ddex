import json
import openai
import random
from os import path
import argparse
import re

using_weighted = True
n = 40 #@param {type:"number"}

def get_args():
	user_prompt, batch_size = 'a boy', 40
	artist1, artist2, artist3, artist4, modifier1, modifier2, modifier3, modifier4 = "", "", "", "", "", "", "", ""
	artist1weight, artist2weight, artist3weight, artist4weight = 0,0,0,0
	modifier1weight, modifier2weight, modifier3weight, modifier4weight = 0,0,0,0
	user_use_result = True
	parser = argparse.ArgumentParser()
	parser.add_argument("prompt", help="the base prompt (comma seperate each weighted section")
	parser.add_argument("-a1", "--artist1", help="name of first artist")
	parser.add_argument("-a2", "--artist2", help="name of second artist")
	parser.add_argument("-a3", "--artist3", help="name of third artist")
	parser.add_argument("-a4", "--artist4", help="name of fourth artist")
	parser.add_argument("-a1w", "--artist1weight", type = int, help="name of first artist weight")
	parser.add_argument("-a2w", "--artist2weight", type = int, help="name of second artist weight")
	parser.add_argument("-a3w", "--artist3weight", type = int, help="name of third artist weight")
	parser.add_argument("-a4w", "--artist4weight", type = int, help="name of fourth artist weight")	
	parser.add_argument("-m1", "--modifier1", help="name of first modifier")
	parser.add_argument("-m2", "--modifier2", help="name of second modifier")
	parser.add_argument("-m3", "--modifier3", help="name of third modifier")
	parser.add_argument("-m4", "--modifier4", help="name of fourth modifier")
	parser.add_argument("-m1w", "--modifier1weight", type = int, help="name of first modifier weight")
	parser.add_argument("-m2w", "--modifier2weight", type = int, help="name of second modifier weight")
	parser.add_argument("-m3w", "--modifier3weight", type = int, help="name of third modifier weight")
	parser.add_argument("-m4w", "--modifier4weight", type = int, help="name of fourth modifier weight")
	parser.add_argument("-n", "--noresult", action="store_true", help="reduce the number of words in the apkg")

	args = parser.parse_args()
	user_prompt = args.prompt

	if args.artist1:
		artist1 = args.artist1
	if args.artist2:
		artist2 = args.artist2
	if args.artist3:
		artist3 = args.artist3
	if args.artist4:
		artist4 = args.artist4

	if args.artist1weight:
		artist1weight = args.artist1weight
	if args.artist2weight:
		artist2weight = args.artist2weight
	if args.artist3weight:
		artist3weight = args.artist3weight
	if args.artist4weight:
		artist4weight = args.artist4weight

	if args.modifier1:
		modifier1 = args.modifier1
	if args.modifier2:
		modifier2 = args.modifier2
	if args.modifier3:
		modifier3 = args.modifier3
	if args.modifier4:
		modifier4 = args.modifier4

	if args.modifier1weight:
		modifier1weight = args.modifier1weight
	if args.modifier2weight:
		modifier2weight = args.modifier2weight
	if args.modifier3weight:
		modifier3weight = args.modifier3weight
	if args.modifier4weight:
		modifier4weight = args.modifier4weight

	if args.noresult:
		user_use_result = False	

	return (user_prompt, batch_size, artist1, artist2, artist3, artist4, modifier1, modifier2, modifier3, modifier4,
		artist1weight, artist2weight, artist3weight, artist4weight,	modifier1weight, modifier2weight, 
		modifier3weight, modifier4weight, user_use_result)



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
	return finished_section

def rand_w():
	to_ret = ":"+str(random.randint(1,10))
	return (to_ret)

(user_prompt, batch_size, artist1, artist2, artist3, artist4, modifier1, modifier2, modifier3, modifier4,
	artist1weight, artist2weight, artist3weight, artist4weight,	modifier1weight, modifier2weight, 
	modifier3weight, modifier4weight, user_use_result) = get_args()

for j in range(n):
	prompt = ''	
	if using_weighted:		
		prompt = """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """ + user_prompt
	artist_section = construct_section(artists)
	result = ""
	if user_use_result: 
		response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=30, stop= "\n")
		result = response["choices"][0]["text"].strip()
	if not result.strip():
		#print('000')
		prompt_to_append = '["'+user_prompt +'",' + artist_section + ',"trending on Artstation"]'
	if using_weighted:
		weighted_result = result.replace(',',(rand_w()+'", "')).replace('.',(rand_w()+'", "'))
		user_prompt_formatted = ''
		if weighted_result and weighted_result[-1] != '"':
			weighted_result = weighted_result + rand_w()+'", '
			user_prompt_formatted = user_prompt+ ' '
		else:
			user_prompt_formatted = user_prompt + rand_w()+'", '
		if user_prompt_formatted[-3] == '"':
			weighted_result = '"'+weighted_result
		prompt_to_append = '["'+user_prompt_formatted + weighted_result + construct_section(artists) + construct_section(modifiers) + '"trending on Artstation'+rand_w()+'"]'
	prompt_to_append = prompt_to_append.replace('""', '"').replace('" ', '"')
	prompt_to_append = re.sub(' +', ' ', prompt_to_append)
	prompts.append(prompt_to_append)

for item in prompts:
	print(item.replace('""','"'),",")

#todo

#make a check for each finished line to see if it is valid, if not then delete it?
#	maybe a non-issue now
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
#find out how to do gpt3 with a blank before it
#add new pics to ddex
#make ratings
#rate all picks


#it could be set up to take an entire prompt and then give a bunch of variations on it

#@markdown _For collaboration and updates, email to martin.kallstrom@gmail.com_