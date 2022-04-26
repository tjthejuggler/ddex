#import libraries of other peoples code
import os #file locations and directories
import json #deals with json files
import tkinter as tk #to create GUIs(Graphical User Interfaces) in python
from os.path import exists #file locations and directories
from profanity_filter import ProfanityFilter #used censoring
from PIL import Image #show images

def build_image_catalog():
	pf = ProfanityFilter()  #set up our sensor(to maybe be used later)
	censored = False
	directory = './directories' #tells us where our images and settings(jsons) files are
	image_data_objects = [] #empty list
	for subdir, dirs, files in os.walk(directory): #looping through every folder and every file in ./directories
		for filename in files: #we do the following things to every file it finds
			this_path_to_the_file = os.path.join(subdir, filename) # set the file path to a text variable
			settings_file_name = filename.split('_')[0] + "_settings.txt"
			if filename.endswith(".png") and exists(this_path_to_the_file.split(filename)[0]+settings_file_name):	#check to see if this file in an image(png) and if it has a settings txt file		
				#if both these conditions are met, then we continue, if not we move on to the next file
				with open(this_path_to_the_file.split(filename)[0]+settings_file_name, 'r') as f: #we open the text(settings/json) file
					use_this_image = True #we are going to add this image to our app
					data = json.load(f) #gets the text from the settings file
					text = f.read()
					if type(data.get('text_prompts')) is dict:
						data['text_prompts'] = str(data['text_prompts']["0"])
					else:
						data['text_prompts'] = str(data['text_prompts'])
					json_object = {
						"path": this_path_to_the_file,
						"text": data
					}
					for item in data['text_prompts']:
						if censored and pf.is_profane(item):
							print(item)
							use_this_image = False
					if use_this_image: #if we are using this image, then we add its information to our image_data_objects list
						image_data_objects.append(json_object)
	return image_data_objects

#this function gets created now, but it will be used later
def get_filtered_images(user_input, image_data_objects): #goes through all the text files that match the images that we are going to use
	images_prompt_list = []
	images_path_list = []
	for data in image_data_objects: #we loop through each text file
		#print('1', data['text'])
		if user_input.lower() in data['text']['text_prompts'].lower():
			result = json.dumps(data['text']['text_prompts']) # we look at the prompts
			images_path_list.append(data['path'])
			images_prompt_list.append(result)
	images_path_list, images_prompt_list = (list(t) for t in zip(*sorted(zip(images_path_list, images_prompt_list))))
	return images_path_list, images_prompt_list

#design our GUI(graphical user interface)
class ExampleApp(tk.Tk):
	def __init__(self, image_data_objects):
		def image_chosen_by_user(*args):
			index_of_selected_item = self.images_listbox.curselection()[0]
			path_of_currently_selected_item = self.images_path_list[index_of_selected_item]
			im = Image.open(path_of_currently_selected_item)
			im.show()
			self.data.configure(state="normal")
			self.data.delete('1.0', tk.END)
			self.data.insert("end", "test")
			self.data.configure(state="disabled")

		def update_main_prompt_list(*args): #filters our image list based on the users entry
			self.images_listbox.delete(0, tk.END)
			self.images_path_list, self.image_prompts_list = get_filtered_images(self.users_search_text.get(), image_data_objects)
			for ind,prompt in enumerate(self.image_prompts_list):	
				self.ending = '('+self.images_path_list[ind].split('(')[1]
				self.images_listbox.insert("end", prompt + self.ending+'\n')
			return True	

		def click_data_reset(*args):
			print('click_data_reset')
			self.data.configure(state="normal")
			self.data.delete('1.0', tk.END)

		def click_data_save(*args):
			print('click_data_save')

		def click_postdata_reset(*args):
			print('click_postdata_reset')
			self.postdata.configure(state="normal")
			self.postdata.delete('1.0', tk.END)

		def click_postdata_save(*args):	
			print('click_postdata_save')

		self.images_path_list = []   
		self.image_prompts_list = []
		tk.Tk.__init__(self) #required thing for making a tkinter GUI

		#widget that shows prompt/image list
		image_prompts_list_variable = tk.StringVar(value=())
		self.images_listbox = tk.Listbox(self, listvariable=image_prompts_list_variable, width=400, height=10, selectmode='extended')
		self.images_listbox.pack(fill="both", expand=True)
		self.images_listbox.bind("<Return>", image_chosen_by_user)
		self.images_listbox.bind('<Double-Button>', image_chosen_by_user)

		self.users_search_text = tk.StringVar()
		self.users_search_text.trace_add('write', update_main_prompt_list) #'update_main_prompt_list' gets run whenever the users_search_text entry changes 
		self.user_entry = tk.Entry(self, bd =5, textvariable=self.users_search_text) #actually create our entry
		self.user_entry.pack(side="bottom", fill="x") #add our entry to our tkinter window
		
		self.data_window= tk.Toplevel(self) #require tkinter line
		self.data = tk.Text(self.data_window, wrap="word", width=400, height=25, cursor="xterm #0000FF")
		self.data.pack(side="top", fill="x")
		
		self.data_reset = tk.Button(self.data_window, text="data reset", command=click_data_reset)#maybe getting rid of self. fixed this, test print
		self.data_reset.pack(side="top", fill="x")
		
		self.data_save = tk.Button(self.data_window, text="data save", command=click_data_save)
		self.data_save.pack(side="top", fill="x")
		
		self.postdata = tk.Text(self.data_window, wrap="word", width=400, height=25, cursor="xterm #0000FF")
		self.postdata.pack(side="top", fill="x")
		
		self.postdata_reset = tk.Button(self.data_window, text="postdata reset", command=click_postdata_reset)
		self.postdata_reset.pack(side="top", fill="x")
		
		self.postdata_save = tk.Button(self.data_window, text="postdata save", command=click_postdata_save)
		self.postdata_save.pack(side="top", fill="x")

		update_main_prompt_list()

if __name__ == "__main__":
	image_data_objects = build_image_catalog()
	print("Count:", len(image_data_objects)) #show us how many images we are able to use
	app = ExampleApp(image_data_objects)
	app.mainloop()

# #this needs worked on
# 	my_option_menu.configure(window, user_choice, *updated_list)

# from tkinter import *

# search_options = [list(myDict.keys())] #etc

# master = Tk()

# variable = StringVar(master)
# variable.set(search_options[0]) # default value

# w = OptionMenu(master, variable, *search_options)
# w.pack()


#mainloop()

