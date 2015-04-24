# TCP client example
import socket,os,time,json,base64,hashlib,select,trigger,uuid,sys

MAX_MSG_SIZE = 512000
SERVER_IP = "192.168.1.80"
SERVER_PORT = 9875
mid=str(uuid.getnode())
pw=124
h = hashlib.new('ripemd160')
h.update(str(pw).encode("UTF-8"))
logged_in=0
file_uploading=""
msg_q=[]
file_q=[]
client_socket=""
last_transfer=time.time()

#******************************************************#
def trigger_handle(event,data):
	global msg_q
	if(event=="uploading"):
		file_q.append(data)
	elif(event=="state_change"):
		msg={}
		msg["cmd"]=event
		msg["state"]=data
		msg_q.append(msg)
#******************************************************#
def upload_file(data):
	#print(str(time.time())+" -> this is upload_file with "+path)
	path=data[0]
	ts=data[1]

	global logged_in
	if(logged_in!=1):
		print("We can't upload as we are not logged in")
		return -1
	img = open(path,'rb')
	i=0
	while True:
		strng = img.read(MAX_MSG_SIZE-100)
		if not strng:
			break

		msg={}
		msg["cmd"]="wf"
		msg["fn"]=path
		msg["data"]=base64.b64encode(strng).decode('utf-8')
		msg["sof"]=0
		if(i==0):
			msg["sof"]=1
		msg["eof"]=0
		msg["msg_id"]=i	
		msg["ack"]=-1
		msg["ts"]=ts
		if(len(strng)!=(MAX_MSG_SIZE-100)):
			msg["eof"]=1
		#print('sending('+str(i)+') of '+path+'...')
		msg_q.append(msg)
		#msg=json.dumps(msg)	
		#client_socket.send(msg.encode("UTF-8"))
		i=i+1
	#print(str(time.time())+' all messages for '+path+' are in buffer.. i guess')
	img.close()
	return 0
	# end of while
#******************************************************#
def connect():
	print("[A "+time.strftime("%H:%M:%S")+"] -> connecting ...")
	c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		c_socket.connect((SERVER_IP, SERVER_PORT))
	except:
		print("Could not connect to server")
		print("retrying in 3 sec")
		time.sleep(3)
		return -1

	print("[A "+time.strftime("%H:%M:%S")+"] -> connected. Loggin in...")

	#### login 
	msg={}
	msg["mid"]=mid
	msg["client_pw"]=h.hexdigest()
	msg["cmd"]="login"	
	msg["ts"]=time.strftime("%d.%m.%Y || %H:%M:%S")
	msg["ack"]=-1
	msg_q.append(msg)
	#msg=json.dumps(msg)
	#client_socket.send(msg.encode("UTF-8"))
	#data=client_socket.recv(1024)
	#try:
	#	enc=json.loads(data.decode("UTF-8"))
	#except:
	#	enc=""
	#if(type(enc) is dict):
	#	if(enc.get("cmd")=="login"):
	#		if(enc.get("ok")==1):
	#			logged_in=1
	#			print("logged in")
	#### login 
	return c_socket

# Main programm
#******************************************************#

trigger.start()
trigger.subscribe_callback(trigger_handle,"")
#trigger.set_interval(10)
#trigger.set_interval(1)

comm_wait=0
waiter=[]
hb_out=0
recv_buffer=""

while 1:
	logged_in=0
	client_socket=connect()	
	while(client_socket!=""):
		time.sleep(0.1)
		#************* receiving start ******************#		
		try:
			ready_to_read, ready_to_write, in_error = select.select([client_socket,sys.stdin], [client_socket,], [], 5)
		except:
			print("select detected a broken connection")
			break

		## react on keydown
		if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
			input=sys.stdin.readline()
			if(input[:1]=="q"):
				print("Quit")
				os._exit(1)
				
		## react on msg in
		if(len(ready_to_read) > 0):
			#print("one process is ready")
			try:
				data = client_socket.recv(MAX_MSG_SIZE)
				data_dec = data.decode("UTF-8")
				#print("Data received:"+str(recv))
			except:
				print('client_socket.recv detected error')
				break;
			
			comm_wait=0
			data_dec=recv_buffer+data_dec
			data_array=data_dec.split('}')
		
			for a in range(0,len(data_array)-1):
				data_array[a]+='}'

				try:
					enc=json.loads(data_array[a])
				except:
					enc=""
					print("json decode failed on:"+data_array[a])
					break;
			
				if(type(enc) is dict):
					#print("json decoded msg")
					#print(enc)
					if(enc.get("cmd")=="login"):
						if(enc.get("ok")==1):
							logged_in=1
							print("[A "+time.strftime("%H:%M:%S")+"] -> log-in OK")
						else:
							logged_in=0
							print("[A "+time.strftime("%H:%M:%S")+"] -> log-in failed")
					elif(enc.get("cmd")=="hb"):
						last_transfer=time.time()
						hb_out=0
						print("[A "+time.strftime("%H:%M:%S")+"] -> connection OK")
					elif(enc.get("cmd")=="set_detection"):
						print("setting detection to "+str(enc.get("state")))
						trigger.set_detection(enc.get("state"))
					elif(enc.get("cmd")=="wf"):
						ignore=1
					elif(enc.get("cmd")=="set_interval"):
						print("setting interval to "+str(int(enc.get("interval",0))))
						trigger.set_interval(int(enc.get("interval",0)))
					else:
						print("unsopported command:"+enc.get("cmd"))
				#end of "if"
			# end of "for"

			if(data_array[len(data_array)-1]==""):
				#if data contained a full message and ended with closing tag, we a$
				recv_buffer=""
			else:
				# but if we grabbed something like 1.5 messages, we should buffer $
				recv_buffer=data_array[len(data_array)-1]
				#print("using buffer!")
		#************* receiving end ******************#
		
		#************* timeout check start ******************#
		if(time.time()-last_transfer>60 and hb_out==0):
			print("[A "+time.strftime("%H:%M:%S")+"] -> checking connection")
			msg={}
			msg["cmd"]="hb"
			msg_q.append(msg)
			hb_out=1
		#************* timeout check end ******************#

		#************* file preperation start ******************#
		if(len(file_q)>0):
			file=file_q[0]
			file_q.remove(file)
			upload_file(file)
		#************* file preperation end ******************#

		#************* sending start ******************#
		if(len(msg_q)>0 and (comm_wait==0 or logged_in!=1)):
			msg=""
			#print("We have "+str(len(msg_q))+" waiting...")
			if(logged_in!=1):
				for msg_i in msg_q:
					if(msg_i["cmd"]=="login"):
						print("[A "+time.strftime("%H:%M:%S")+"] -> sending login")
						msg=msg_i
						msg_q.remove(msg_i)
			else:
				msg=msg_q[0]
				msg_q.remove(msg)
			
			if(msg!=""):
				#print("A message is ready to send")
				send_msg=json.dumps(msg)
				if(json.loads(send_msg).get("cmd"," ")=="wf"):
					if(json.loads(send_msg).get("sof",0)==1):
						print("[A "+time.strftime("%H:%M:%S")+"] -> uploading "+json.loads(send_msg).get("fn"))
						file_upload_start=time.time()
				try:
					client_socket.send(send_msg.encode("UTF-8"))
				except:
					client_socket=""
					print("init reconnect")
					break
				#print("message send")
				if(json.loads(send_msg).get("ack",0)==-1):
					#print("waiting on response")
					comm_wait=1
				if(json.loads(send_msg).get("cmd"," ")=="wf"):
					if(json.loads(send_msg).get("eof",0)==1):
						print("[A "+time.strftime("%H:%M:%S")+"] -> uploading "+json.loads(send_msg).get("fn")+" done")
						#print("[A "+time.strftime("%H:%M:%S")+"] -> upload took:"+str(time.time()-file_upload_start))
						#print("[A "+time.strftime("%H:%M:%S")+"] -> ctime:"+str(time.time()-json.loads(send_msg).get("ts",0)))

		#else:
		#************* sending end ******************#
	print("connection destroyed, reconnecting")		
		
#exit()
