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

last_ACK = 0
start_Timer = 0
timer_Timeout = 0
base = 0
nextSeq = 0
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 20832)   
packet_size = 1024
window_Size = 3
print >> sys.stderr, ' \n********* Starting up on %s port %s *********' % server_address
server_socket.bind(server_address)


file = open("C:\\Users\\sayal\\Desktop\\Spiderman.jpg", 'rb')
sum = 0

buffer = bytearray(os.path.getsize("C:\\Users\\sayal\\Desktop\\Spiderman.jpg"))
file.readinto(buffer)
length = len(buffer)
No_Of_Packets = length / data_Size

def cal_Local_Checksum(msg):
    Local_checksum =''.join([bin(~0)[3:] if x == '0' else bin(~1)[4:] for x in msg])
    return Local_checksum

def deassembleACK_Packet(recv_packet):
    ack_received = recv_packet[0:16]
    ack_Checksum = recv_packet[16:33]
    return ack_received, ack_Checksum

def cal_Checksum(packet_no):
    startPosition = packet_no * 1024
    endPosition = startPosition + 1024
    
    k = startPosition
    m = startPosition + 1
    maxLimit = startPosition + 511
    
    sum = bin(0)
    sum = str(sum)[2:].zfill(16)
    
    for i in range (startPosition, endPosition-1, 2):
        byte = buffer[k:m]        
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
     
    checksum =''.join([bin(~0)[3:] if x == '0' else bin(~1)[4:] for x in sum])
    return checksum

def cal_expected_ACK(i):
    if(i % 2 == 0):
        expected_ack = '0000000000000000'
    else:
        expected_ack = '1111111111111111'
    return expected_ack

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


def MakePacket_GBN(packet_No):
    startPosition = packet_No * 1024
    endPosition = startPosition + 1024
    data = buffer[startPosition:endPosition]
    data = str(data)
    print >> sys.stderr , "packet no = %s" %packet_No
    sq_bin = bin(packet_No)
    sq_bin = str(sq_bin)[2:]
    sq_bin = sq_bin.zfill(16)
    print >> sys.stderr , "sq_bin = %sq_bin" %sq_bin

    
    checksum = cal_Checksum(packet_No)
    checksum = str(checksum)

    packet = [data, checksum, sq_bin]
    packet = ''.join(packet)
    return packet

def th_send(client_address):
    global start_Timer
    global base
    global nextSeq
    global last_ACK
    global timer_Timeout
    
    N = 0
    while ((N < No_Of_Packets+1)):
        print >> sys.stderr, "\nN = %s" %N
        print >> sys.stderr , "\ninside thread send"
        if((base == nextSeq ) & (timer_Timeout != 1)):
            for i in range(3):
                pack = MakePacket_GBN(N)
                sent = server_socket.sendto(pack, client_address)
                nextSeq = nextSeq + 1

            start_Timer = 1

        else:
            print >> sys.stderr , "\n base = %s" %base
            print >> sys.stderr, "\n nextSeq = %s" %nextSeq
            
            while(nextSeq < (base + window_Size) & (timer_Timeout != 1)):
                pack = MakePacket_GBN(N)
                sent = server_socket.sendto(pack, client_address)
                nextSeq = nextSeq + 1
                
        if(timer_Timeout == 1):
            print >> sys.stderr , "\n timer expired detected"
            N = base + 1
            pack = MakePacket_GBN(N)
            sent = server_socket.sendto(pack, client_address)
            nextSeq = nextSeq + 1           
        N = N + 1

    
def th_receive(client_address):
    i = 0
    global base
    global last_ACK
    global timer_Timeout

    print >> sys.stderr , "\ninside thread receive"
    data, client_address = server_socket.recvfrom(packet_size)
    print >> sys.stderr , "\n data outside while = %s" %data

    while(data):
        print >> sys.stderr, "data = %s" %data

        if(timer_Timeout == 1):
            print >> sys.stderr, "\n skip acks now"
        else:
            print >> sys.stderr , "\ntimer is yet to expire"
            data = int(data, 2)
            print >> sys.stderr , "\ndata_int = %s" %data
            print >> sys.stderr, "\nlast_ACK = %s" %last_ACK
            
            if(data == last_ACK +1):
                '''print >> sys.stderr , "\npack %s received correctly" >> last_ACK'''
                base = base + 1
                print >> sys.stderr , " \nbase = %s" %base
                last_ACK = data
            else:
                print >> sys.stderr , "\nneed to retransmit"
        data, client_address = server_socket.recvfrom(packet_size)


def th_timer(client_address):
    global start_Timer
    global timer_Timeout
    
    print >> sys.stderr, "\ninside thread timer"
    if(start_Timer == 1):
        print >> sys.stderr, "\nI m going to sleep"
        sleep(5)
        timer_Timeout = 1
        print >> sys.stderr, "\nI woke up after 3 sec"
        start_Timer = 0
    
    
def No_Error(client_address):
    print >> sys.stderr , "\ninside function"
    t1_send = Thread(target=th_send, args=(client_address,))
    t2_timer = Thread(target=th_timer, args=(client_address,))
    t3_receive = Thread(target=th_receive, args=(client_address,))

    t1_send.start()
    t2_timer.start()
    t3_receive.start()

    t1_send.join()
    t2_timer.join()
    t3_receive.join()

    
bClose = 0
bExit = 1
while (bClose != 1 & bExit == 1):
    print >> sys.stderr, 'Sender ready to accept request from receiver'
    data, client_address = server_socket.recvfrom(packet_size)
    print >>sys.stderr, 'Receiver is tring to ping:  "%s"' % data

    message = "\n\t Type 1: Without bit errors \n \t Type 2: Bit errors \n \t Type 3: Errors in acknowledgement from receiver \n \t Type 4: ACK Packet Loss \n \t Type 5: Data Packet loss \n \t Type 6: Exit \n\t Type 7: GBN"
    sent = server_socket.sendto(message, client_address)
    
    data, client_address = server_socket.recvfrom(packet_size)
    print >>sys.stderr, 'Receiver has selected option: "%s"' % data

    message = 'Option %s Selected by receiver' %data
    sent = server_socket.sendto(message, client_address)
    

    if (data == '1'):
        No_Error(client_address)
        print >> sys.stderr ,"End of Option 1"

        
server_socket.close()
        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
