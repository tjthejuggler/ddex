#in python loop through all text files in ./directories and all subdirectories and save each one as a json object
import os
import json

directory = './directories/'
json_objects = []

#for each file in the directory
for subdir, dirs, files in os.walk(directory):
	for filename in files:    	
		if filename.endswith(".txt"):
			#open the file
			this_path = os.path.join(subdir, filename)
			with open(this_path, 'r') as f:
				#read the file

				data = json.load(f)

				text = f.read()
				#create a json object
				json_object = {
					"path": this_path,
					"text": data
				}
				#append the json object to the list of json objects
				json_objects.append(json_object)
				#print the filename
				print(filename)
				# #print the text
				# print(text)
				# #print the json object
				# print(json_object)
				# #print the list of json objects
				# print(json_objects)
				# #print a new line
				print("\n")

def get_filtered_images(user_input):
	images_prompt_list = []
	images_path_list = []
	for data in json_objects:
		print('1', data['text'])
		#print('2', data['text']['tv_scale'])
		for item in data['text']['text_prompts']:
			if user_input in item:
				result = json.dumps(data['text']['text_prompts'])
				images_path_list.append(data['path'])
				images_prompt_list.append(result)
	return images_path_list, images_prompt_list

# #print the list of json objects
# print(len(json_objects))

# from tkinter import *

# top = Tk()
# L1 = Label(top, text="User Name")
# L1.pack( side = LEFT)
# E1 = Entry(top, bd =5)
# E1.pack(side = RIGHT)

# #sv = StringVar()

# def callback(*args):
#     print(var.get())
#     get_filtered_images(var.get())
#     L2.config(text=var.get())
#     return True

# var = StringVar()
# var.trace_add('write', callback)

# e = Entry(top, textvariable=var)
# e.pack()

#         self.text = tk.Text(self, wrap="word", width=40, height=8)
#         self.text.pack(fill="both", expand=True)
#         self.text.bind("<1>", self.on_text_button)
#         for n in range(1,20):
#             self.text.insert("end", "this is line %s\n" % n)

# top.mainloop()

import tkinter as tk

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
			for prompt in self.image_prompts:
				self.text.insert("end", prompt + '\n')
			#self.text.config(text="this")
			
			return True		

		self.user_text.trace_add('write', callback)            
		self.user_entry = tk.Entry(self, bd =5, textvariable=self.user_text)
		self.user_entry.pack(side="bottom", fill="x")
#DiscoTime(41)_settings.txt

		self.img = tk.PhotoImage(file='./directories/DiscoTime/DiscoTime(16)_0000.png')
		self.preview = tk.Label(self, image=self.img)
		self.preview.pack(side="bottom", fill="x")



	def on_text_button(self, event):
		index = self.text.index("@%s,%s" % (event.x, event.y))
		line, char = index.split(".")
		line = str(int(line) - 1)
		print('kkk', line)
		print('lll', self.text.get(line+".0", tk.END))
		self.status.configure(text=self.text.get(line+".0", line+".0 lineend"))
		#self.img = tk.PhotoImage(self.images_path_list[int(line)][:size - 13])
		self.img = tk.PhotoImage(file=self.images_path_list[int(line)][:len(self.images_path_list[int(line)]) - 13]+'_0000.png')
		#self.preview.configure(image=self.img)
		if self.img.width()>1200 or self.img.height()>800:
			self.img = self.img.subsample(2)

		self.preview.configure(image=self.img,borderwidth=4, relief="ridge")
		#self.preview.image = self.img
		
		#print(self.images_path_list[int(line)][:size - 13])



if __name__ == "__main__":
	app = ExampleApp()
	app.mainloop()

#make a github from this
#make capslock not matter
#make search field selectable
#move stuff over from google drive, and put all github stuff inside of it
#make same promp items have # at the end of them	