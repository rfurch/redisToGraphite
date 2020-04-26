#!/usr/bin/python3.6

# libraries we will need

import argparse
import getopt
import sys
import redis
import time
import json
import socket
import pickle
import struct

# global variable for verbosity level
_verbose=0

# default CARBON port for 'pickle' mode (batch insert)
CARBON_PICKLE_PORT = 2004

#--------------------------------------------------------------------------------


def redisToGraphite():

	sock = socket.socket()
	sock.connect( (socket.gethostbyname("carbonServer"), CARBON_PICKLE_PORT) )

	# Redis client with encoding
	r = redis.Redis(socket.gethostbyname("redisServer"), encoding='iso-8859-1')	  # redisServer in etc/hosts

	count = 0   # we will introduce a short delay ever N elements in Redis list

	# get every element from LIST, then from HASH
	tuples = ([])

	for i in r.smembers('devices_bw_list'):
		try:
			count = count + 1
			id = i.decode('utf-8')
			aux = r.hgetall(id)
			[ifID, descr, ibw, obw, cirCom, cirTec, lastSNMP] = r.hmget(id, 'ifID', 'descr', 'ibw', 'obw', 'cirCom', 'cirTec', 'lastSNMP')
			if (_verbose > 2):
				print(r.hmget(id, 'ifID', 'descr', 'ibw', 'obw', 'cirCom', 'cirTec', 'lastSNMP'))

			# build message to insert into Graphite

			now = int(time.time())
			if (_verbose > 1):
				print (ifID, now - int(lastSNMP.decode('utf-8')) )

			# detect elements not interrogated more than 180 seconds ago...  
			if ( (now - int(lastSNMP.decode('utf-8'))) > 180 ):
				if (_verbose > 0):
					print ("Not Active:", id, descr, (now - int(lastSNMP.decode('utf-8'))) )
				outgoingTraffic = -1	
				incomingTraffic = -1	
			else:
				outgoingTraffic = float(obw.decode('utf-8'))/1000
				incomingTraffic = float(ibw.decode('utf-8'))/1000
				
			tagName = "trafficData." + ifID.decode('utf-8') + ".ibw"
			tuples.append((tagName, (now, incomingTraffic)))

			tagName = "trafficData." + ifID.decode('utf-8') + ".obw"
			tuples.append((tagName, (now, outgoingTraffic)))

			tagName = "trafficData." + ifID.decode('utf-8') + ".cirtec"
			tuples.append((tagName, (now, float(cirTec.decode('utf-8')))))

			tagName = "trafficData." + ifID.decode('utf-8') + ".circom"
			tuples.append((tagName, (now, float(cirCom.decode('utf-8')))))

			if ((count % 20) == 0):    # we will 'pcak' info for performace 
	
				if (_verbose > 3):
					print(tuples)
				package = pickle.dumps(tuples, 1)
				size = struct.pack('!L', len(package))
				sock.sendall(size)
				sock.sendall(package)
				tuples = ([])
				time.sleep(0.1)        # basic delay for CPU comsumption
				sock.close()
				sock = socket.socket()
				sock.connect( (socket.gethostbyname("carbonServer"), CARBON_PICKLE_PORT) )

		except TypeError as e:
    		    print(e)


	# send the rest (final part) of elements, as we use MOD(N) to 
	# split large list in 'chunks' 

	try:
		package = pickle.dumps(tuples, 1)
		size = struct.pack('!L', len(package))
		sock.sendall(size)
		sock.sendall(package)
		tuples = ([])

	except TypeError as e:
		print(e)

	return(0)

#--------------------------------------------------------------------------------

def main():
	global _verbose

	try:
		opts, args = getopt.getopt(sys.argv[1:], "i:c:vh", ["help", "verbose"])
	except getopt.GetoptError as err:
		# print help information and exit:
		print (str(err))  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-v", "--verbose"):
			_verbose+=1
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
#		elif o in ("-i"):
#			IPAddress = a
		else:
			assert False, "unhandled option"
		
	redisToGraphite()
	sys.exit()

#--------------------------------------------------------------------------------

def usage():
	print ("\n\n")
	print ("Read REDIS HASH for traffic bandwidth and send data to GRAPHITE")
	print ("-v [Optional verbosity level.  the more 'v' the more verbose!]")
	print ("-h [Print this message]")
	print ("\n\n")

#--------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
    
#--------------------------------------------------------------------------------
