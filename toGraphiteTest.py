#!/usr/bin/python3.6

import redis
import time
import json
import socket

# Redis client with encoding
r = redis.Redis('localhost', encoding='iso-8859-1')

# get every element from LIST, then from HASH
count = 0

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003

for i in r.smembers('devices_bw_list'):
	try:
		count = count + 1
		if ((count % 100) == 0):    # basic delay for CPU comsumption
			time.sleep(0.2)
		id = i.decode('utf-8')
		aux = r.hgetall(id)
		[ifID, descr, ibw, obw, cirCom, cirTec] = r.hmget(id, 'ifID', 'descr', 'ibw', 'obw', 'cirCom', 'cirTec')

# build message to insert into Graphite

		if ( int(ifID) == 7):

			sock = socket.socket()
			sock.connect((CARBON_SERVER, CARBON_PORT))

			meassure = "trafficData"
			msgTxt = "trafficData." + ifID.decode('utf-8') + ".upload " + ibw.decode('utf-8') + " " + str(int(time.time())) + "\n"
			sock.sendall(msgTxt.encode())
			print(msgTxt)	
			msgTxt = "trafficData." + ifID.decode('utf-8') + ".download " + obw.decode('utf-8') + " " + str(int(time.time())) + "\n"
			sock.sendall(msgTxt.encode())
			print(msgTxt)	
			msgTxt = "trafficData." + ifID.decode('utf-8') + ".circom " + cirCom.decode('utf-8') + " " + str(int(time.time())) + "\n"
			sock.sendall(msgTxt.encode())
			print(msgTxt)	
			msgTxt = "trafficData." + ifID.decode('utf-8') + ".cirtec " + cirTec.decode('utf-8') + " " + str(int(time.time())) + "\n"
#			sock.sendto(bytes(msgTxt, "utf-8"), ("127.0.0.1", 2003))
#			sock.sendall(bytes(msgTxt, "utf-8"))
			sock.sendall(msgTxt.encode())
			print(msgTxt)	
		
			sock.close()

	except TypeError as e:
    	    print(e)



