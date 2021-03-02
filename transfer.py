import socket 
import sys 
import netifaces
import time
import glob

# global vars
HEADERSIZE = 20

# helper functions
def get_ip():
    return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
    if not ip.startswith("127.")][:1], [[(s.connect(('1.1.1.1', 53)),
    s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
    socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

done = True
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '10.25.10.18' # IP of server that will recieve, not this device
port = 12352

location = "/home/pi/final/"
vidset = [file for file in glob.glob(location + "videos/encrypted/*", recursive=False)]
keyset = [file for file in glob.glob(location + "keys/*", recursive=False)]
if len(vidset) != len(keyset):
    print("Video and keyfiles are not properly matched")
    exit()

def is_interface_up(interface):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr

while done:
	if is_interface_up('wlan0'):
		IPAddr = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
		print(IPAddr)
		if IPAddr == get_ip():
                    #try:
                        s.connect((host, port))

                        for i in range(len(vidset)): 
                            # send video
                            viddata = open(vidset[i], 'r').read()
                            viddata = f"{len(viddata):<{HEADERSIZE}}" + viddata
                            s.send(bytes(viddata, "utf-8"))
                            #send key
                            keydata = open(keyset[i], 'r').read()
                            keydata = f"{len(keydata):<{HEADERSIZE}}" + keydata
                            s.send(bytes(keydata, "utf-8"))
                            print("Sent data (" + str(i+1) + "/" + str(len(vidset)) + ")")
                           
                        done = False
                    #except:
                        #host = input("(WIP, just press enter and change var) If host is not at ip {host}, please type in host v4 IP. Otherwise press enter to abort.")
                        #done = False
		else:
			print('IP address of client (this device) is undetermined.')
			time.sleep(120)
	else:
		print('No connection, please allow this device to access local router or internet. Attempting connection again in 5 seconds. Press Ctrl+C to stop exit.')
		time.sleep(5)
print('Done.')

