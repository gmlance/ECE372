from socket import * 
import os 
import sys 
import struct 
import time 
import select 
import binascii  

ICMP_ECHO_REQUEST = 8 
 
def checksum(string):  
 csum = 0 
 countTo = (len(string) // 2) * 2   
 count = 0 
 #bytearray ex:
  #in:
   #size = 5
   #arr = bytearray(size)
   #print(arr)
  #out:
   #bytearray(b'\x00\x00\x00\x00\x00')
 string = bytearray(string)
 #turns the input string into a bytearray. I found this fixed the errors.

 #because of bytearray type remove ord typecast
 #for count in range(0, countTo, 2):
 while count < countTo:
  # or 13<<8 shift 8 bits. makes it so you can make an 8 bit word
  # ex: 13, A1 --> 0001 0011, 1010 0001 & 13<<8 --> 0001001100000000 + 10100001 --> 0001001110100001
  thisVal = string[count+1] * 256 + string[count]  
  csum = csum + thisVal  
  csum = csum & 0xffffffff   
  count = count + 2 
  
 if countTo < len(string): 
  csum = csum + string[len(string) - 1] 
  csum = csum & 0xffffffff  

 csum = (csum >> 16) + (csum & 0xffff) 
 csum = csum + (csum >> 16) 
 #answer = 0xFFFF - (csum & 0xFFFF)
 answer = ~csum  
 answer = answer & 0xffff  
 answer = answer >> 8 | (answer << 8 & 0xff00) 

#the four fs mean 16 ones 0xffff
#answer = 0xFFFF - (csum 0xFFFF) for negative value issues.
#Check transmission using wireshark. Checksum grabbing structure bracket?
 # b'\.....\...' 
 # how to fix: check the struct type being given to checksum 
 #there was probably an update to python that broke this function
 #the fix I found was to typecast the checksum to a bytearray. Doing this,
 #the operations from the skeleton code worked. 

 return answer


def receiveOnePing(mySocket, ID, timeout, destAddr): 
 timeLeft = timeout 
  
 while 1:  
  startedSelect = time.time() 
  whatReady = select.select([mySocket], [], [], timeLeft) 
  howLongInSelect = (time.time() - startedSelect) 
  if whatReady[0] == []: # Timeout 
   return "Request timed out." 
  
  timeReceived = time.time()  
  recPacket, addr = mySocket.recvfrom(1024) 

  #START

  icmpHeader = recPacket[20:28]
  icmpType, code, mychecksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
  #struct.unpack unpacks the information held in the buffer
    
  if type != 8 and packetID == ID:
   bytesInDouble = struct.calcsize("d")
   timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
   return timeReceived - timeSent

  #END

  timeLeft = timeLeft - howLongInSelect 
  if timeLeft <= 0: 
   return "Request timed out." 
  
def sendOnePing(mySocket, destAddr, ID): 
 # Header is type (8), code (8), checksum (16), id (16), sequence (16) 
  
 myChecksum = 0 
 # Make a dummy header with a 0 checksum 
 # struct -- Interpret strings as packed binary data 
 header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 
 # ">" forced condition. "d" os standard -> not always the same
 data = struct.pack('d', time.time()) 
 # Calculate the checksum on the data and the dummy header. 

 myChecksum = checksum(header + data) 
  
 # Get the right checksum, and put in the header 
 if sys.platform == 'darwin': 
  # Convert 16-bit integers from host to network  byte order 
  myChecksum = htons(myChecksum) & 0xffff   
 else: 
  myChecksum = htons(myChecksum) 
   
 header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 

 #header = struct.pack("BBHHH", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 
 
 packet = header + data 
  
 mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str 
 # Both LISTS and TUPLES consist of a number of objects 
 # which can be referenced by their position number within the object. 
  
def doOnePing(destAddr, timeout):  
 icmp = getprotobyname("icmp") 
 # SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw 
 
 #mySocket = socket(AF_INET, SOCK_RAW, icmp) 
 mySocket = socket(AF_INET, SOCK_DGRAM, icmp) 
 #Using this different socket removes the permission errors

 myID = os.getpid() & 0xFFFF  # Return the current process i 
 sendOnePing(mySocket, destAddr, myID) 
 delay = receiveOnePing(mySocket, myID, timeout, destAddr) 
  
 mySocket.close() 
 return delay 

def ping(host, name, timeout=1): 
 #initialize a counter so the ping program will exit on its own.
 #initialize an empty list to hold the ping time data
 loopcount = 0
 timedata = []
 # timeout=1 means: If one second goes by without a reply from the server, 
 # the client assumes that either the client's ping or the server's pong is lost 
 dest = gethostbyname(host) 
 print("__________________________________________________________________________________________")
 print("Pinging " + dest + " using Python:") 
 print("__________________________________________________________________________________________") 
 # Send ping requests to a server separated by approximately one second 
 try:
  while loopcount < 5: 
   delay = doOnePing(dest, timeout) 
   print("Delay from: ",name, " from IP/DNS: ", dest,  " is ", delay, " in milliseconds")
   timedata.append(delay) 
   time.sleep(1)# one second
   loopcount = loopcount + 1 
  #average value of a list based on its length
  avg_value = 0 if len(timedata) == 0 else sum(timedata)/len(timedata)
  print("__________________________________________________________________________________________")
  print("avg/max/min times (in milliseconds) from ",name, ":")
  print(avg_value,"/", max(timedata),"/", min(timedata))
  print("__________________________________________________________________________________________")
 except KeyboardInterrupt:
  #if interrupted print avg/max/min for data we have
  timedata.remove(0)
  avg_value = 0 if len(timedata) == 0 else sum(timedata)/len(timedata)
  print("__________________________________________________________________________________________")
  print("avg/max/min times (in milliseconds) from ",name, ":")
  print(avg_value,"/", max(timedata),"/", min(timedata))
  print("__________________________________________________________________________________________")

 return delay

#------------------------------------------------------------------------------
#//////////////////////////////////////////////////////////////////////////////
# Enter Domain Names/IP addresses to ping below
# Format: ping("IP/Domain Name", "Label/IP Name")
# Note: the "Label/IP Name" is just a label for the Data --> It can be anything
# Note: Default number of pings set to 5.
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#------------------------------------------------------------------------------

#Three Examples

#ping localhost (myself from the access point)
#me --> access point --> me
ping("127.0.0.1", "Localhost")

#ping google
#names will be handled by DNS
ping("www.google.com", "Google")

#ping University of Bristol (in the UK)
ping("137.222.0.38", "University of Bristol")