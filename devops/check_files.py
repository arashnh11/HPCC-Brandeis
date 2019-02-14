# Author: Arash Nemati Hayati
# 14 Feb 2019
# HPCC Brandeis

#This code will 
	#1) check for files and folders inside a given path and will generate a report
    	#listing those users that have files that have not been accessed/modified/group_changed
		# within the given time threshold
	#2) notify users about the files and ask them to transfer/remove them within 7 days of receiving the notice

import os, time, datetime
import pwd, smtplib
import email.message
import random
import smtplib
import sys

clear = lambda: os.system('clear')
clear()

# This function will return the group and user for a given file
class FILE:
	def __init__(self, filepath):
		self.path=filepath
		self.user=pwd.getpwuid(os.stat(filepath).st_uid).pw_name
		self.group=pwd.getpwuid(os.stat(filepath).st_uid).pw_name
		self.email=self.user+'@brandeis.edu'

# This function will notify users of their files
def send_email(user,time_thresh,file,sample_access):
	sender = 'hayati@hpcc.brandeis.edu'
	receivers = user+'@brandeis.edu'
	sender_name='HPCC Brandeis' 
	sender_email='<no-reply@hpcc.brandeis.edu>'
	receiver_name=user
	receiver_email='<'+user+'@brandeis.edu>'
	subject='Important Notice: Your Data on $WORK'
	body='Dear HPCC user: '+user+'\n\n'+'Our records show that you have files on $WORK that have not been accessed/changed/modified in the last '+str(time_thresh)+' days.'+' Below is a sample of such files:\n'+file+' '+sample_access+'\n\n'+'We kindly ask you to review those files and either delete them or transfer them to long-term storage spaces at your research lab or personal space in the next 7 days from receiving this notice. Otherwise, they will be deleted without any further notice.'+' For more details regarding HPCC user policies please visit https://kb.brandeis.edu/display/SCI/HPCC+User+Policies.\n\nThank you for your cooperation\nHigh-Performance-Computing Center Administration\nDivision of Science, Brandeis University'
	message = """From: %s %s
To: %s %s
Subject: %s
%s
""" % (sender_name, sender_email, receiver_name, receiver_email, subject, body)
	smtpObj = smtplib.SMTP('hpcphi.sci.brandeis.edu')
	smtpObj.sendmail(sender, receivers, message)      

# This function will create a report of the files summary at a given path	
def create_report(database, time_thresh, time_now, filepath):
	date=str(time_now.year)+"-"+str(time_now.month)+"-"+str(time_now.day)
	file = open("work_summary-"+date,"w") 
	file.write("#This file reports user/group owners of all files on "+str(filepath)+" that have not been accessed in the last "+str(time_thresh)+" days.\n")
	file.write("#Report Date: "+date+"\n")
	file.write("#Format: user_owner group_owner sample_file last_access elapsed_time_since_last_access\n\n")
	for key in database:
		file.write("%s %s %s %s %2.0f\n" %(key, database[key][0], database[key][1], database[key][2], database[key][3]))
	file.close()

# This function will walk through all files in a given path recursively
def file_search(filepath, time_thresh,time_now):
	database={}
	for (dirpath, dirnames, filenames) in os.walk(filepath):
		dir = FILE(dirpath)
		if dir.user in database or dirpath.find('.snapshot') != -1 or len(filenames) == 0:
			continue
		# select a random file inside each folder
		f = random.sample(filenames,1)
		if f[0][0] == '.':
			continue
		# get the absolute path of the file
		file=dirpath+'/'+f[0]
		# Get the file ownership information
		F = FILE(file)		
		if F.user in database:
			continue
		# last time the file ownership was changed
		last_own=os.stat(file).st_ctime # in date-hh-mm-ss format
		time_own=time.ctime(last_own) # in seconds format
		# last time the file was changed
		last_mod=os.stat(file).st_mtime # in date-hh-mm-ss format
		time_mod=time.ctime(last_mod) # in seconds format
		# last time the file was accessed 
		last_acc=os.stat(file).st_atime # in date-hh-mm-ss format
		time_acc=time.ctime(last_acc) # in seconds format
		# convert current time to seconds
		stamp_now=datetime.datetime.timestamp(time_now)
		# find the time difference between now and the last file changes
		diff_own = stamp_now - last_own # file owenership change
		diff_mod = stamp_now - last_mod # file modification
		diff_acc = stamp_now - last_acc # file access
		# Find the minimum time difference between now and last file change
		diff_min = min(diff_acc,diff_mod,diff_own) / (24 * 3600) # in days
		# Find the latest time change of the file
		time_max = max(time_acc,time_own,time_mod)
		# Count the number of files that each user/group has that has exceeded the criteria
		if (diff_min > time_thresh):
			if not F.user in database:
				database[F.user] = [F.group, F.path, time_max, diff_min]
				print("%s %s %s %2.0f" %(F.group, F.path, time_max, diff_min))
	return database
def main():
	# current time
	time_now=datetime.datetime.now()
	# time period criteria to check whether the last time the file was changed is beyond the time threshold
	time_thresh=int(sys.argv[1]) # in days
	# filepath
	filepath=str(sys.argv[2])
	# Run the file search function and create the database
	database=file_search(filepath, time_thresh,time_now)
	create_report(database,time_thresh,time_now, filepath)
	# Notify users by email
	for key in database:
		send_email(key, time_thresh, database[key][1], database[key][2])
if __name__ == '__main__':
	main()
