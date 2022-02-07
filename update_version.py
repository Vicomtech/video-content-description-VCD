# This is a Python script which updates the version number of the VCD files
# Usage: >python update_version.py <new_version>
#   The script investigates which is the current version (in vcd.version) and replaces it with <new_version>
#   e.g. >python update_version.py "5.0.1"
# Author: Marcos Nieto

import os
import sys
import glob
import subprocess

replace = True  # flag used during the development of this script to check things work as expected

def replace_in_files(extensions, version_old, version_new):
    for extension in extensions:
        files = [fn for fn in glob.iglob('**/*' + extension, recursive=True) if ((not 'node_modules' in fn) and (not 'd.ts' in fn))]

        #for filename in glob.iglob('**/*' + extension, recursive=True):            
        for filename in files:
            with open(file=filename, mode='r+') as f:
                text = f.read()
                new_text = text.replace(version_old, version_new)
                
                if text == new_text:
                    print('\t' + filename + ' ------- no ' + version_old)
                else:
                    print('\t' + filename + ' replacing ' + version_old + ' with ' + version_new)

                if replace:                    
                    f.seek(0)
                    f.write(new_text)
                    f.truncate()                

# Read user input
if(len(sys.argv) != 2):
    print("ERROR: Please provide a valid new version number, e.g.: 5.0.1")
assert(len(sys.argv) == 2)
version_new = sys.argv[1]

# Check version
with open(file="vcd.version") as f:
    version_current = f.readlines()[0] 
    print("Current version is {version_current}".format(version_current=version_current))

if version_current == version_new:
    print("Current version is already " +  version_new)

else:
    # User confirmation
    warning_message = "Confirm you want to modify VCD version from {version_current} to {version_new} (y/n): ".format(version_current=version_current, version_new=version_new)
    val = input(warning_message)
    if val == "y" or val == "Y":
        print("Proceeding to replace {} with {}".format(version_current, version_new))

        # Update files
        extensions = ['.py', '.ts']
        replace_in_files(extensions, version_current, version_new)

        # package.json and package-lock.json should not be touched by this script: dependencies' versions may be coincident with vcd version
        print('Remember to modify manually package.json at \\nodejs and then: npm run build, npm install')

        # At the end, update vcd.version
        extensions = ['.version']
        replace_in_files(extensions, version_current, version_new)

        # Run updating documentation (only valid for Windows)
        subprocess.check_call(["pdoc", "--html", "--output-dir", ".\\doc\\pdoc", ".\\vcd", "--force"])  # this will create doc\pdoc

    else:
        print("Cancelled by user.")





