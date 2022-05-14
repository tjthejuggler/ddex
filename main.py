#import libraries of other peoples code
import os #file locations and directories
import json #deals with json files
import tkinter as tk #to create GUIs(Graphical User Interfaces) in python
from os.path import exists #file locations and directories
from profanity_filter import ProfanityFilter #used censoring
from PIL import ImageTk, Image


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

		def expandToBound(image_width, image_height):
			bounding_width = 840
			bounding_height = 670
			width_scale = 0
			height_scale = 0

			width_scale = bounding_width / image_width
			height_scale = bounding_height / image_height 

			scale = min(width_scale, height_scale)

			new_width, new_height = int(image_width * scale), int(image_height * scale)
			return new_width, new_height
		

		def image_highlighted_by_user(*args):
			full_path = self.images_path_list[self.images_listbox.curselection()[0]]
			filename = os.path.basename(full_path)
			print("filename",filename)
			directory_only = full_path.split(filename)[0]
			settings_file_name = filename.split('_')[0] + "_settings.txt"
			print('directory_only+settings_file_name', directory_only+settings_file_name)
			with open(directory_only+settings_file_name, 'r') as f:
				text_file_contents = f.read()
			self.data.configure(state="normal")
			self.data.delete(1.0, tk.END)
			self.data.insert(tk.END, full_path)
			self.data.insert(tk.END, text_file_contents)
			self.data.configure(state="disabled")
			self.image_for_coords = ImageTk.Image.open(full_path)
			self.image_for_coords_width, self.image_for_coords_height = self.image_for_coords.size
			self.original = Image.open(full_path)
			self.new_width, self.new_height = expandToBound(self.image_for_coords_width, self.image_for_coords_height)
			self.resized = self.original.resize((self.new_width, self.new_height),Image.ANTIALIAS)
			self.img = ImageTk.PhotoImage(self.resized)
			# self.resized = self.img.resize((800, 600),Image.ANTIALIAS)
			self.imglabel.configure(image=self.img)
			self.imglabel.image = self.img

		self.images_path_list = []   
		self.image_prompts_list = []
		tk.Tk.__init__(self) #required thing for making a tkinter GUI

		#widget that shows prompt/image list
		image_prompts_list_variable = tk.StringVar(value=())
		self.images_listbox = tk.Listbox(self, listvariable=image_prompts_list_variable, width=400, height=18)
		self.images_listbox.pack(fill="both", expand=True)
		self.images_listbox.bind("<Return>", image_chosen_by_user)
		self.images_listbox.bind('<Double-Button-1>', image_chosen_by_user)
		self.images_listbox.bind('<<ListboxSelect>>', image_highlighted_by_user)

		self.users_search_text = tk.StringVar()
		self.users_search_text.trace_add('write', update_main_prompt_list) #'update_main_prompt_list' gets run whenever the users_search_text entry changes 
		self.user_entry = tk.Entry(self, bd =5, textvariable=self.users_search_text) #actually create our entry
		self.user_entry.pack(side="bottom", fill="x") #add our entry to our tkinter window

		self.data_window= tk.Toplevel(self) #require tkinter line
		self.data_window.geometry('1000x670+0+320')
		self.data = tk.Text(self.data_window, wrap="word", width=400, height=25, font=('Times New Roman',15))
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

		self.image_window= tk.Toplevel(self) #require tkinter line
		self.image_window.geometry('840x670+1075+320')

		self.frame = tk.Frame(self.image_window, width=840, height=670)
		self.frame.pack()
		self.frame.place(anchor='center', relx=0.5, rely=0.5)

		self.img = ImageTk.PhotoImage(Image.open("./directories/DiscoTime/images_out/A100/DiscoTime(10)_0000.png"))

		self.imglabel = tk.Label(self.frame, image = self.img)
		self.imglabel.pack()

		update_main_prompt_list()

if __name__ == "__main__":
	image_data_objects = build_image_catalog()
	print("Count:", len(image_data_objects)) #show us how many images we are able to use
	app = ExampleApp(image_data_objects)

	app.mainloop()