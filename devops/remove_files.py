import os, time, datetime
import pwd, smtplib
import email.message
clear = lambda: os.system('clear')
clear()

# This function will return the group and user for a given file
class FILE:
	def __init__(self, filepath):
		self.path=filepath
		self.user=pwd.getpwuid(os.stat(filepath).st_uid).pw_name
		self.group=pwd.getpwuid(os.stat(filepath).st_uid).pw_name
		self.email=self.user+'@brandeis.edu'

def send_email(admin,user,address,textfile):
	with open(textfile) as fp:
		msg=email.message.EmailMessage()
		msg.set_content(fp.read())
	msg['Subject']='The contents of %s' % textfile
	msg['From']=admin
	msg['To']=user	
	s=smtplib.SMTP(host='localhost', port=1025)
	s.send_message(msg)
	s.quit()
def create_report(database, time_thresh, time_now):
	date=str(time_now.year)+"-"+str(time_now.month)+"-"+str(time_now.day)
	file = open("work_summary-"+date,"w") 
	file.write("#This file reports user/group owners of all files on /work that have not been accessed in the last "+str(time_thresh)+" days.\n")
	file.write("#Report Date: "+date+"\n")
	file.write("#Format: user_owner group_owner number_of_files\n\n")
	for key in database:
		file.write("%s %s %d\n" %(key, database[key][1], database[key][0]))
	file.close() 
# This function will walk through all files in a given path recursively
def file_search(filepath, time_thresh,time_now):
	date=str(time_now.year)+"-"+str(time_now.month)+"-"+str(time_now.day)
	list_files = open("work_files-"+date,"w") 
	list_files.write("#This file reports all files on /work that have not been accessed in the last "+str(time_thresh)+" days.\n")
	list_files.write("#Report Date: "+date+"\n")
	list_files.write("#Format: file elapsed_time_from_last_access(in days) last_access user_owner group_owner\n\n")
	
	database={}
	for (dirpath, dirnames, filenames) in os.walk(filepath):
		if dirpath.find('.') == -1:
			for f in filenames:
				if f[0] != '.':
					# get the absolute path of the file
					file=dirpath+'/'+f
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
					# Get the file ownership information
					F = FILE(file)		
					# Count the number of files that each user/group has that has exceeded the criteria
					if (diff_min > time_thresh):
						if F.user in database:
							database[F.user][0] += 1
						else:
							database[F.user] = [1, F.group]
						list_files.write("%s %2.1f %s %s %s\n" % (F.path, diff_min, time_max, F.user, F.group))
	list_files.close()
	return database
def main():
	# current time
	time_now=datetime.datetime.now()
	# time period criteria to check whether the last time the file was changed is beyond the time threshold
	time_thresh=30 # in days
	# filepath
	filepath=os.getcwd()
	filepath='/work/dayakaran/'
	# Run the file search function and create the database
	database=file_search(filepath, time_thresh,time_now)
	report=create_report(database,time_thresh,time_now)
	# Send Email to users
if __name__ == '__main__':
	main()
