import sys,  threading, time
from clients import m2m_state,det_state

__author__ = 'kolja'
#******************************************************#

def subscribe_callback(fun):
	if callback[0]==subscribe_callback:
		callback[0]=fun
	else:
		callback.append(fun)
#******************************************************#

class poe:
	def __init__(self,s,n,d,state):
		self.shortcut =s  	# e.g. U
		self.name=n		# e.g. Upload
		self.description = d	# e.g. Shows the filename of every upload
		self.state = state	# e.g. active
	def set_state(self,state):
		self.state=state

#******************************************************#


def start():
	threading.Thread(target = start_listen, args = ()).start()

def start_listen():
	print_out.append(poe("h","Heartbeats","Shows the Heartbeats of every M2M client",1))
	print_out.append(poe("r","Rulemanager","Rulemanager output",1))
	print_out.append(poe("u","Uploades","Shows every uploaded file",1))

	while(1):
		input=sys.stdin.readline()
		input=input[0:len(input)-1] # strip newline
		if(len(input)==0):
			continue
		
		if(input[0]=="_" and len(input)>=3): #activate or deactivate outputs
			found=0
			for a in print_out:
				if(input[1]==a.shortcut):
					if(int(input[2])==1):
						a.state=1
						print("switched output of '"+a.description+"' on")
						found=1
						break
					elif(int(input[2])==0):
						a.state=0
						print("switched output of '"+a.description+"' off")
						found=1
						break
			if(input[1]=="_"):
				show_status()
				found=1
			elif(input[1]=="a"):
				state=-1
				found=1
				if(int(input[2])==1):
					state=1
				elif(int(input[2])==0):
					state=0
				if(state!=-1):
					for a in print_out:
						a.state=state
					if(state):
						print("switched all output on")
					else:
						print("switched all output off")
				

			if(not(found)):
				print("")
				print("I haven't understood you sequece, possible sequences are:")
				print("_a for all")
				for a in print_out:
					print("_"+str(a.shortcut)+" for '"+str(a.description)+"'")
				print("followed by '1' or '0'")
				print("")

		else:
			callback[0](input)

def rint(input,sc):
	found=0
	for a in print_out:
		if(a.shortcut==sc):
			found=1
			if(a.state==1):
				print(input)
	if(not(found)):
		print("didn't recogice shortcut '"+sc+"'")	

def show_m2m(id,l,m2m):
	if(id==-2):
		print("-------------------------------------------------------------------------------------------------------------------------------------------------------")
		print("we got "+str(l)+" m2m-clients connected")
	elif(id==-1):
		print("M2M (short mid/alias) | Account    | Detection | State         | IP             | l-in | last_seen  | Area            | Coordinates")
		print("-------------------------------------------------------------------------------------------------------------------------------------------------------")
	elif(id==0):
		p_alias=(m2m.alias+"               ")[0:15]
		p_account=(m2m.account+"               ")[0:10]
		p_ip=(str(m2m.ip)+"                  ")[0:14]
		p_area=(str(m2m.area)+"                  ")[0:15]
		if(m2m.detection>=0):
			p_detection=(det_state[m2m.detection]+"           ")[0:9]
		else:
			p_detection=(str(m2m.detection)+"                  ")[0:9]
		p_state=(m2m_state[int(m2m.state)]+"                   ")[0:13]
		output=str(m2m.mid)[-5:]+"/"+p_alias+" | "+p_account+" | "+str(p_detection)+" | "+(p_state)+" | "+str(p_ip)+" | "+str(m2m.logged_in)+"    | "
		output+=str(int(m2m.last_comm))+" | "+p_area+" | "+str(m2m.latitude)+"/"+str(m2m.longitude)
		print(output)
	elif(id==1):
		print("-------------------------------------------------------------------------------------------------------------------------------------------------------")



def show_status():
	for a in print_out:
		print("Shortcut '"+a.shortcut+"' for "+a.name+" is "+str(a.state))

callback = [subscribe_callback]
print_out =[]
