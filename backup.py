import os
import time
import sys
'''
Simple program that accepts paths as input to backup to zip

Input: Accepts any number of Source folders

Ouput: Creates a destination folder with the current date and makes a backup with current time name
'''

source = []

for i in sys.argv:
	source.append(i)

if not (len(sys.argv) > 1):
	print 'No source to backup', len(sys.argv)
	sys.exit()
target_dir = './Backup_dir'

if not os.path.exists(target_dir):
	os.mkdir(target_dir)

today = target_dir + os.sep +time.strftime('%Y%m%d')

now = time.strftime('%H%M%S')

comment = raw_input('Enter a commit message: ')

if len(comment) == 0:
	target = today + os.sep + now + '.zip'
else:
	target = today + os.sep + now + '_'+ comment.replace(' ', '_') + '.zip'

if not os.path.exists(today):
	os.mkdir(today)
	print '{} directory created'.format(today)

zip_command = "zip -r -q {0} {1}".format(target,' '.join(source))

print "Zip command is:"
print zip_command
print "Running:"

if os.system(zip_command) == 0:
	print 'Success in backup to', target
else:
	print 'backup failed'
