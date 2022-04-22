import os
from pathlib import Path
from os import listdir
from os.path import isfile, join

#this is a script that renames all files in a directory to lowercase

cwd = os.getcwd()
parent_dir = cwd+'/directories/DiscoTime/images_out/'


#onlyfiles = [f for f in listdir(parent_dir) if isfile(join(parent_dir, f))]

for subdir, dirs, files in os.walk(parent_dir):
	for filename in files:    	
		this_path = os.path.join(subdir, filename)
		if '0000-100_' in this_path:
			os.rename(this_path, this_path.replace('0000-100_', '0'))

		

# with open( parent_dir, 'w') as fd:
#     os.replace(old_name, new_name, src_dir_fd=fd)