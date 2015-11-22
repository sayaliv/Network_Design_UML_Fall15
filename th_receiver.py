import socket
from socket import AF_INET, SOCK_DGRAM
import sys
import os
import struct
from binascii import hexlify
from time import sleep
import random
import select
from threading import Thread

received_Packet = -1
packet_size = 1024
buff = 1060
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 20884)

print >> sys.stderr , "************Client started***********"

def get_bit(byteval, index):
    if((byteval&(1<<index))!=0):
        return 1
    else:
        return 0
    
def get_op1_ready(byteval):
    h = hexlify(byteval)
    num = int(h, 16)
    num1 = bin(num)
    num1 = str(num1)[2:]
    num1 = num1.zfill(16)
    return num1

def cal_Checksum_for_received_data(data):
    sum = bin(0)
    sum = str(sum)[2:].zfill(16)
    
    k = 0
    m = 1
    
    for i in range (0, 1023, 2):
        byte = data[k:m]        
        num1 = get_op1_ready(byte)
        sum = bin(int(sum,2) + int(num1,2))
        sum = str(sum)[2:].zfill(16)
        chk = get_bit(int(sum,2), 16)

        if(chk == 1):
            carry = bin(1)
            carry = str(carry)[2:].zfill(16)
            sum = bin(int(sum,2) + int(carry,2))
            offset = '0b10000000000000000'
            sum = bin(int(sum,2) - int(offset,2))
            sum = str(sum)[2:].zfill(16)

        k = k + 2
        m = m + 2
    return sum

def cal_Local_Checksum(a):
    a = [str(a)]
    a = ''.join(a)
    Local_checksum =''.join([bin(~0)[3:] if x == '0' else bin(~1)[4:] for x in a])
    return Local_checksum

def add_Checksum(c1, c2): # Function to perform bit wise addition on 16 bits
    c3 = bin(int(c1,2) + int(c2,2))
    c4 = hex(int(c3,2))

    if (c4 == '0xffff'):
        c5 = '1'
    else:
        c5 = '0'
    return c5

def th_send():
    print >> sys.stderr , "inside th_send"

def th_receive():
    global received_Packet
    print >> sys.stderr , " received_Packet = %s" %received_Packet
    print >> sys.stderr, "inside th_receive"
    f_name = manage_FileNames()
    print >> sys.stderr ,"f_name = %s" %f_name  
    file = open(f_name, 'wb')
    data, server = client_socket.recvfrom(buff)
    i = 0
    while(data):
        if(data == 'EOF'):
            file.close()
            data = 0
        else:
            print >> sys.stderr, "\n New packet arrived = %s" %i
            i = i + 1
            file_data = data[0:1024] # extract file data
            chksum_calulated = cal_Checksum_for_received_data(file_data)#calculate checksum of received data
            chksum_received = data[1024:1040]# checksum received from sender
            is_Success = add_Checksum(chksum_received, chksum_calulated)
            sq_receive = data[1040:1056]
            sq_int = int(sq_receive, 2)
            print >> sys.stderr , " sq_int = %s" %sq_receive
            if(is_Success):
                if(received_Packet + 1 == sq_int):
                    file.write(file_data)
                    print >> sys.stderr , " received_Packet = %s" %received_Packet
                    received_Packet = sq_int
                    print >> sys.stderr , " received_Packet = %s" %received_Packet
                    sent = client_socket.sendto(sq_receive, server_address)
                    print >> sys.stderr , " sq send = %s" %sq_receive

            else:
                print >> sys.stderr , " do not send ack"
                i = i - 1

        data, server = client_socket.recvfrom(buff)
    
def N0_Errors():
    print >> sys.stderr , "inside function"
    t1_receive1= Thread(target=th_receive, args=())

    t1_receive1.start()
    t1_receive1.join()
    
def manage_FileNames():
    f_name = "C:\\Users\\sayal\\Downloads\\new_test.jpg"
    base_name = os.path.basename(f_name)
    d = os.path.splitext(base_name)
    path = "C:\\Users\\sayal\\Downloads\\"
    k = 0
    dupFlag = 0
    while(os.path.isfile(f_name)):
        k = k + 1
        new_fname = d[0]+'_'+str(k)+d[1]
        name = path+new_fname
        f_name = name
    return f_name

bClose = 0
bExit = 1
while (bClose != 1 & bExit == 1):
    message = raw_input("Receiver tries to ping server : ")    
    sent = client_socket.sendto(message, server_address)

    print >>sys.stderr, 'Receiver waiting for reply'
    data, server = client_socket.recvfrom(1041)
    print >>sys.stderr, 'Sender Says: "%s"' % data

    if(data == 'Option 1 Selected by receiver'):
        N0_Errors()
        
client_socket.close()        
        
print >> sys.stderr, 'Receiver connection is closed'
