import json
import openai
import random
from os import path
import argparse
import re

using_weighted = True
n = 4 #@param {type:"number"}

def get_args():
	user_input, batch_size = 'a boy', 4
	artist1, artist2, artist3, artist4, style1, style2, style3, style4 = "", "", "", "", "", "", "", ""
	artist1weight, artist2weight, artist3weight, artist4weight = 0,0,0,0
	style1weight, style2weight, style3weight, style4weight = 0,0,0,0
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
	parser.add_argument("-m1", "--style1", help="name of first style")
	parser.add_argument("-m2", "--style2", help="name of second style")
	parser.add_argument("-m3", "--style3", help="name of third style")
	parser.add_argument("-m4", "--style4", help="name of fourth style")
	parser.add_argument("-m1w", "--style1weight", type = int, help="name of first style weight")
	parser.add_argument("-m2w", "--style2weight", type = int, help="name of second style weight")
	parser.add_argument("-m3w", "--style3weight", type = int, help="name of third style weight")
	parser.add_argument("-m4w", "--style4weight", type = int, help="name of fourth style weight")
	parser.add_argument("-n", "--noresult", action="store_true", help="reduce the number of words in the apkg")

	args = parser.parse_args()
	user_input = args.prompt

	# if args.artist1:
	# 	artist1 = args.artist1
	# if args.artist2:
	# 	artist2 = args.artist2
	# if args.artist3:
	# 	artist3 = args.artist3
	# if args.artist4:
	# 	artist4 = args.artist4

	# if args.artist1weight:
	# 	artist1weight = args.artist1weight
	# if args.artist2weight:
	# 	artist2weight = args.artist2weight
	# if args.artist3weight:
	# 	artist3weight = args.artist3weight
	# if args.artist4weight:
	# 	artist4weight = args.artist4weight

	# if args.style1:
	# 	style1 = args.style1
	# if args.style2:
	# 	style2 = args.style2
	# if args.style3:
	# 	style3 = args.style3
	# if args.style4:
	# 	style4 = args.style4

	# if args.style1weight:
	# 	style1weight = args.style1weight
	# if args.style2weight:
	# 	style2weight = args.style2weight
	# if args.style3weight:
	# 	style3weight = args.style3weight
	# if args.style4weight:
	# 	style4weight = args.style4weight

	# if args.noresult:
	# 	user_use_result = False	

	return (user_input, batch_size)



styles_file = open( "prompgen_styles.txt", "r")
styles = styles_file.readlines()
styles_file.close()

artists_file = open( "prompgen_artists.txt", "r")
artists = artists_file.readlines()
artists_file.close()

prompts_file = open( "prompgen_prompts.txt", "r")
pre_prompts = prompts_file.readlines()
prompts_file.close()

#@markdown Get your GPT-3 API key from https://openai.com

openai.api_key = "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" #@param {type:"string"}

prompts = []

def rand_item(my_list):
	intro = ''
	if my_list == artists:
		intro = 'by '
	return intro+random.choice(my_list).strip()

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
	to_ret = str(random.randint(1,10))
	return (to_ret)

def get_result(user_prompt):
	prompt = ''	
	if using_weighted:		
		prompt = """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ random.choice(pre_prompts) + """
	* """+ user_prompt
	response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=30, stop= "\n")
	result = response["choices"][0]["text"].strip()
	result = result.replace(',',(":"+rand_w()+'", "')).replace('.',(":"+rand_w()+'", "'))
	return result


(user_input, batch_size) = get_args()


user_prompt = ''

print('user_input', user_input)


for i in range(batch_size):
	prompt_to_append = ''
	for section in user_input.split(","):

		if len(prompt_to_append) > 1: #if we have already been through once, then make a ,
			prompt_to_append = prompt_to_append + ","
		prompt_to_append = prompt_to_append + '"'
		if section[0] == "$": #style is used
			prompt_to_append = prompt_to_append + rand_item(styles)
		elif section[0] == "@": #artist is used
			prompt_to_append = prompt_to_append + rand_item(artists)
		elif section[0] == ":":
			if section[-1] == ":": #if the char after the : is not a digit, then
				prompt_to_append = prompt_to_append + rand_item(random.choice([artists,styles]))+":"+rand_w()+'"'
		else:
			if ">" in section and section[0] != ">":
				user_prompt = section.split(">")[0]
				result = get_result(user_prompt)
				prompt_to_append = prompt_to_append + user_prompt+' '+result
				if section[-1] == ":":
					prompt_to_append = prompt_to_append + ":"+rand_w()
				prompt_to_append = prompt_to_append + ":"+rand_w()+'"'

			else:
				if ":" in section:
					prompt_to_append = prompt_to_append + section.split(":")[0]
					if section[-1] == ":":
						prompt_to_append = prompt_to_append + ":"+rand_w()+'"'
				else:
					prompt_to_append = user_input
		if section[0] == "$" or section[0] == "@":
			if len(section) > 1:
				if section[1] == ":" and section[-1] == ":": #if no weight is given, then use a random weight
					prompt_to_append = prompt_to_append + ":"+rand_w()
				else:
					prompt_to_append = prompt_to_append + user_input.split(":")[1]
			prompt_to_append = prompt_to_append + '"'



	print("p",prompt_to_append)

# for j in range(n):
# 	prompt = ''	
# 	if using_weighted:		
# 		prompt = """
# 	* """+ random.choice(pre_prompts) + """
# 	* """+ random.choice(pre_prompts) + """
# 	* """+ random.choice(pre_prompts) + """
# 	* """+ random.choice(pre_prompts) + """
# 	* """+ random.choice(pre_prompts) + """
# 	* """+ user_prompt
# 	artist_section = construct_section(artists)
# 	result = ""
# 	if user_use_result: 
# 		response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=30, stop= "\n")
# 		result = response["choices"][0]["text"].strip()
# 	if not result.strip():
# 		prompt_to_append = '["'+user_prompt +'",' + artist_section + ',"trending on Artstation"]'
# 	if using_weighted:
# 		weighted_result = result.replace(',',(rand_w()+'", "')).replace('.',(rand_w()+'", "'))
# 		user_prompt_formatted = ''
# 		if weighted_result and weighted_result[-1] != '"':
# 			weighted_result = weighted_result + rand_w()+'", '
# 			user_prompt_formatted = user_prompt+ ' '
# 		else:
# 			user_prompt_formatted = user_prompt + rand_w()+'", '
# 		if user_prompt_formatted[-3] == '"':
# 			weighted_result = '"'+weighted_result
# 		prompt_to_append = '["'+user_prompt_formatted + weighted_result + construct_section(artists) + construct_section(styles) + '"trending on Artstation'+rand_w()+'"]'
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
#		choose: prompts and/or prompt weights, and then same with artists and styles)
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



#@markdown _For collaboration and updates, email to martin.kallstrom@gmail.com_

#user tells 
#	how many(or up to how many), -artnumran 3 -artnum 3
#	the names and numbers of any definite ones
#		$ - random style
#		@ - random artists
#		: - if alone, random weight
#		:3 - designated weight of 3
#		this - 'this' with no weight
#		that: - 'that with a random weight'
#		, - seperates prompts
#		,, - the space between these indicates a completely random modifier
#		this is> - 'this is' plus a completion prompt
#		<was clear - a pre completion prompt with 'was clear' after it
#
#example:
#	python3 promgen.py "this is a big>:,@:,@:,$:" 
#		gets gpt3 response with "this is a big", gives it a random weight, then gets 2 artists and a style, 
#			and gives them random weights


#eventually
#	super tags, (portraits, trippy, landscape..)
#		it uses these tags to give certain artists/styles extra likeliness to be selected
