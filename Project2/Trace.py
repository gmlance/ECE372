from socket import *
import socket
import os
import sys
import struct
import time
import select
import binascii
ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2
# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise
def checksum(string):
 str_ = bytearray(string)
 csum = 0
 countTo = (len(string) // 2) * 2

 for count in range(0, countTo, 2):
  thisVal = string[count+1] * 256 + string[count]
  csum = csum + thisVal
  csum = csum & 0xffffffff

 if countTo < len(string):
   csum = csum + string[-1]
   csum = csum & 0xffffffff

 csum = (csum >> 16) + (csum & 0xffff)
 csum = csum + (csum >> 16)
 answer = ~csum
 answer = answer & 0xffff
 answer = answer >> 8 | (answer << 8 & 0xff00)
 return answer
# In this function we make the checksum of our packet
# hint: see icmpPing lab
# In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
# packet to be sent was made, secondly the checksum was appended to the header and
# then finally the complete packet was sent to the destination.
# Make the header in a similar way to the ping exercise.
# Append checksum to the header.
# Don’t send the packet yet , just return the final packet in this function.
# So the function ending should look like this

def build_packet():
#somewhat standard script to build a packet
#grab ID for packet
#build header
#create data
#create checksum
#check platform for checksum compatability
#rebuild header with new checksum (originally zero)
#build packet
#return packet
 myChecksum = 0
 myID = os.getpid() & 0xFFFF
 header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
 data = struct.pack("d", time.time())
 myChecksum = checksum(header + data)    
 if sys.platform == 'darwin':
  myChecksum = socket.htons(myChecksum) & 0xffff
 else:
  myChecksum = htons(myChecksum)
 header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
 packet = header + data
 return packet

def get_route(hostname):
 timeLeft = TIMEOUT
 for ttl in range(1,MAX_HOPS):
  for tries in range(TRIES):
   destAddr = gethostbyname(hostname)
#Fill in start
# Make a raw socket named mySocket
# Basically stolen from ICMPping. These two lines of code grab the icmp constant and initializes the socket under the given constant
   icmp = socket.getprotobyname("icmp")
   #this returns the associated constant for the protocol based on the socket definition
   #ICMP constant is 7 but asking the socket will return whatever constant is defined by its module
#mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
#SOCK_DGRAM --> socket datagram --> this socket uses UDP and gets around thhe permision errors with RAW
#The issues with RAW may come from the fact that it is for "raw network protocol access"
#If TCP is desired SOCK_STREAM can be used
#note: SOCK_STREAM was not tested in this implementation
   mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, icmp)
 #Fill in end
   mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
   mySocket.settimeout(TIMEOUT)
  try:
   d = build_packet()
   mySocket.sendto(d, (hostname, 0))
   t= time.time()
   startedSelect = time.time()
   whatReady = select.select([mySocket], [], [], timeLeft)
   howLongInSelect = (time.time() - startedSelect)
   if whatReady[0] == []: # Timeout
    print(" * * * Request timed out.")
   recvPacket, addr = mySocket.recvfrom(1024)
   print(addr)
   #print the address
   timeReceived = time.time()
   timeLeft = timeLeft - howLongInSelect
   if timeLeft <= 0:
    print(" * * * Request timed out.")
  except timeout:
    continue
  else:
#Fill in start
 #Fetch the icmp type from the IP packet
    icmpHeader = recvPacket[20:28]
    types, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
 #Fill in end
    if types == 11:
     bytes = struct.calcsize("d")
     timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
     print(" %d rtt=%.0f ms %s" %(ttl, (timeReceived -t)*1000, addr[0]))
    elif types == 3:
     bytes = struct.calcsize("d")
     timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
     print(" %d rtt=%.0f ms %s" %(ttl,(timeReceived-t)*1000, addr[0]))
    elif types == 0:
     bytes = struct.calcsize("d")
     timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
     print(" %d rtt=%.0f ms %s" %(ttl, (timeReceived - timeSent)*1000, addr[0]))
     return
    else:
     print("error")
     break
  finally:
    mySocket.close()

print("------------------------------")
print("//////////////////////////////")
print("Tracing route to: www.google.com")                
print("------------------------------")
print("//////////////////////////////")
get_route("www.google.com")
print("------------------------------")
print("//////////////////////////////")
print("Tracing route to: www.youtube.com")                
print("------------------------------")
print("//////////////////////////////")
get_route("www.youtube.com")
print("------------------------------")
print("//////////////////////////////")
print("Tracing route to: www.twitter.com")                
print("------------------------------")
print("//////////////////////////////")
get_route("www.twitter.com")
print("------------------------------")
print("//////////////////////////////")
print("Tracing route to: www.wikipedia.org")                
print("------------------------------")
print("//////////////////////////////")
get_route("www.wikipedia.org")