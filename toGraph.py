#!/usr/bin/python3.6

import redis
import time
import json
import socket
import pickle
import struct

from random import randrange, uniform


CARBON_SERVER = '127.0.0.1'
CARBON_PICKLE_PORT = 2004

sock = socket.socket()
sock.connect( (CARBON_SERVER, CARBON_PICKLE_PORT) )

for i in range(1000):
	tuples = ([])
	now = int(time.time())
	tuples.append(('system.loadavg_1min', (now,uniform(0,14))))
	tuples.append(('system.loadavg_5min', (now,uniform(-3,8))))
	tuples.append(('system.loadavg_15min', (now,uniform(2,4))))
	package = pickle.dumps(tuples, 1)

	size = struct.pack('!L', len(package))
	sock.sendall(size)
	sock.sendall(package)
	time.sleep(0.01)

#carbon = CarbonClient('localhost', 2004)
#pickle = []
#pickle.append(('trafficData.1.upload', (str(int(time.time()))) , 9420.3))
#pickle.append(('trafficData.1.download', (str(int(time.time()))) , 420.3))

#carbon.send_pickle(pickle)






