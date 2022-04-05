#in python loop through all text files in ./directories and all subdirectories and save each one as a json object
import os
import json
import tkinter as tk
from os.path import exists
from profanity_filter import ProfanityFilter

pf = ProfanityFilter()
censored = False
directory = './directories/'
json_objects = []

for subdir, dirs, files in os.walk(directory):
	for filename in files:    	
		this_path = os.path.join(subdir, filename)
		if filename.endswith(".png") and exists(this_path[:-8]+'settings.txt'):			
			with open(this_path[:-8]+'settings.txt', 'r') as f:
				use_this_image = True
				data = json.load(f)
				text = f.read()
				json_object = {
					"path": this_path,
					"text": data
				}
				for item in data['text_prompts']:
					if censored and pf.is_profane(item):
						print(item)
						use_this_image = False
				if use_this_image:
					json_objects.append(json_object)
					print(filename)
					print("\n")

print("Count:", len(json_objects))

def get_filtered_images(user_input):
	images_prompt_list = []
	images_path_list = []
	for data in json_objects:
		print('1', data['text'])
		for item in data['text']['text_prompts']:
			if user_input.lower() in item.lower():
				result = json.dumps(data['text']['text_prompts'])
				images_path_list.append(data['path'])
				images_prompt_list.append(result)
	images_path_list, images_prompt_list = (list(t) for t in zip(*sorted(zip(images_path_list, images_prompt_list))))
	return images_path_list, images_prompt_list

class ExampleApp(tk.Tk):
	def __init__(self):
		self.images_path_list = []
		self.image_prompts = []
		tk.Tk.__init__(self)
		self.status = tk.Label(self, anchor="w")
		self.status.pack(side="bottom", fill="x")
		self.text = tk.Text(self, wrap="word", width=400, height=10, cursor="xterm #0000FF")
		self.text.configure(state="normal")
		self.text.pack(fill="both", expand=True)
		self.text.bind("<1>", self.on_text_button)
		self.user_text = tk.StringVar()
		self.images_path_list, self.image_prompts = get_filtered_images(self.user_text.get())
		for ind,prompt in enumerate(self.image_prompts):
			self.ending = '('+self.images_path_list[ind].split('(')[1]
			self.text.insert("end", prompt + self.ending+'\n')
		#self.text.configure(state="disabled")
		
		def callback(*args):
			#print(self.user_text.get())
			self.text.configure(state="normal")
			self.text.delete('1.0', tk.END)
			self.images_path_list, self.image_prompts = get_filtered_images(self.user_text.get())
			for ind,prompt in enumerate(self.image_prompts):	
				self.ending = '('+self.images_path_list[ind].split('(')[1]
				self.text.insert("end", prompt + self.ending+'\n')
			self.text.configure(state="disabled")
			return True		

		self.user_text.trace_add('write', callback)            
		self.user_entry = tk.Entry(self, bd =5, textvariable=self.user_text)
		self.user_entry.pack(side="bottom", fill="x")
		self.img = tk.PhotoImage(file='./directories/DiscoTime(0)_0000.png')
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

