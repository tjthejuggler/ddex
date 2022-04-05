#in python loop through all text files in ./directories and all subdirectories and save each one as a json object
import os
import json

import tkinter as tk
from os.path import exists


directory = './directories/'
json_objects = []

for subdir, dirs, files in os.walk(directory):
	for filename in files:    	
		#if ends in .png and has_matching settings.txt file
		this_path = os.path.join(subdir, filename)
		print('**', this_path)
		print(this_path[:-8]+'settings.txt')
		if filename.endswith(".png") and exists(this_path[:-8]+'settings.txt'):			
			with open(this_path[:-8]+'settings.txt', 'r') as f:
				data = json.load(f)
				text = f.read()
				#create a json object
				json_object = {
					"path": this_path,
					"text": data
				}
				json_objects.append(json_object)
				print(filename)
				print("\n")

def get_filtered_images(user_input):
	images_prompt_list = []
	images_path_list = []
	for data in json_objects:
		print('1', data['text'])
		#print('2', data['text']['tv_scale'])
		for item in data['text']['text_prompts']:
			if user_input.lower() in item.lower():
				result = json.dumps(data['text']['text_prompts'])
				images_path_list.append(data['path'])
				images_prompt_list.append(result)

	images_path_list, images_prompt_list = (list(t) for t in zip(*sorted(zip(images_path_list, images_prompt_list))))

	# images_prompt_list.sort()			
	# images_path_list = [x for _,x in sorted(zip(images_prompt_list,images_path_list))]
	return images_path_list, images_prompt_list

class ExampleApp(tk.Tk):
	def __init__(self):
		self.images_path_list = []
		self.image_prompts = []
		tk.Tk.__init__(self)
		self.status = tk.Label(self, anchor="w")
		self.status.pack(side="bottom", fill="x")
		self.text = tk.Text(self, wrap="word", width=400, height=10, cursor="xterm #0000FF")
		self.text.pack(fill="both", expand=True)
		self.text.bind("<1>", self.on_text_button)
		for n in range(1,20):
			self.text.insert("end", "this is line %s\n" % n)
		self.user_text = tk.StringVar()
		def callback(*args):
			print(self.user_text.get())
			self.text.delete('1.0', tk.END)
			self.images_path_list, self.image_prompts = get_filtered_images(self.user_text.get())
			for ind,prompt in enumerate(self.image_prompts):
				self.text.insert("end", prompt + self.images_path_list[ind][-13]+'\n')
				
			return True		

		self.user_text.trace_add('write', callback)            
		self.user_entry = tk.Entry(self, bd =5, textvariable=self.user_text)
		self.user_entry.pack(side="bottom", fill="x")
		self.img = tk.PhotoImage(file='./directories/DiscoTime/DiscoTime(16)_0000.png')
		self.preview = tk.Label(self, image=self.img)
		self.preview.pack(side="bottom", fill="x")

	def on_text_button(self, event):
		index = self.text.index("@%s,%s" % (event.x, event.y))
		line, char = index.split(".")
		line = str(int(line) - 1)
		
		path = self.images_path_list[int(line)]
		self.status.configure(text=path)
		self.img = tk.PhotoImage(file=path)
		if self.img.width()>1200 or self.img.height()>800:
			self.img = self.img.subsample(2)
		self.preview.configure(image=self.img,borderwidth=4, relief="ridge")

if __name__ == "__main__":
	app = ExampleApp()
	app.mainloop()

#make search field selectable
	#dropdown that is full of all keys
		#if it is number, then we should accept ranges

#make same prompt items have # at the end of them	

#instead of looking for text files, i should look for completed files that have matching text files, and then i should add 
#	their endings to the 

