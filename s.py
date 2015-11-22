import socket
from socket import AF_INET, SOCK_DGRAM
import sys
import os
import struct
from binascii import hexlify
from time import sleep
import random
import select
import threading

data_Size = 1024
ack = 0
send_buffer = 1042

global base 
global nextSeq
base = 0
nextSeq = 0
window_Size = 5

file = open("C:\\Users\\sayal\\Desktop\\Spiderman.jpg", 'rb')
sum = 0

buffer = bytearray(os.path.getsize("C:\\Users\\sayal\\Desktop\\Spiderman.jpg"))
file.readinto(buffer)
length = len(buffer)
No_Of_Packets = length / data_Size

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 20660)   
packet_size = 1024

def sendFreshWindow(pack_no):
    local_seq = 0
    local_seq = nextSeq
    print >> "local_seq = %s" %local_seq

    print >> sys.stderr , "inside sendFreshWindow, initial pack_no = %s" %pack_no
    server_socket.setblocking(0)

    pack_0 = MakePacket_GBN(pack_no)
    sent = server_socket.sendto(pack_0, client_address)
    pack_no = pack_no + 1
    local_seq = local_seq + 1
    nextSeq = local_seq
    print >> "pack_no = %s" %pack_no
    print >> "nextSeq = %s" %nextSeq

    pack_1 = MakePacket_GBN(pack_no)
    sent = server_socket.sendto(pack_1, client_address)
    pack_no = pack_no + 1
    local_seq = local_seq + 1
    nextSeq = local_seq

    print >> "pack_no = %s" %pack_no
    print >> "nextSeq = %s" %nextSeq

    pack_2 = MakePacket_GBN(pack_no)
    sent = server_socket.sendto(pack_2, client_address)
    pack_no = pack_no + 1
    local_seq = local_seq + 1
    nextSeq = local_seq
    print >> "pack_no = %s" %pack_no
    print >> "nextSeq = %s" %nextSeq

    pack_3 = MakePacket_GBN(pack_no)
    sent = server_socket.sendto(pack_3, client_address)
    pack_no = pack_no + 1
    local_seq = local_seq + 1
    nextSeq = local_seq
    print >> "pack_no = %s" %pack_no
    print >> "nextSeq = %s" %nextSeq

    pack_4 = MakePacket_GBN(pack_no)
    sent = server_socket.sendto(pack_4, client_address)
    pack_no = pack_no + 1
    local_seq = local_seq + 1
    nextSeq = local_seq
    print >> "pack_no = %s" %pack_no
    print >> "nextSeq = %s" %nextSeq

    return pack_no

        
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
    
def GBN(client_address):
    print >> sys.stderr," inside GBN"
    i = 0
    while (97 % 5 < 5):
        server_socket.setblocking(0)
        threads = []
        '''current_Index = sendFreshWindow(i)'''
        for i in range(3):
            
            
        print >> sys.stderr , " current_Index = %s" %current_Index

        ready = select.select([server_socket], [], [], 0.001)
        sleep(0.7)
        try:
            recv_packet, client_address = server_socket.recvfrom(1041)

        except socket.error:
            print >> sys.stderr , "******************timer timed out for ack %s" %i
            recv_packet = 0

        server_socket.setblocking(1)

        if(recv_packet):
            base = base + 1
            ack_received, chksum_received = deassembleACK_Packet(recv_packet)
            print >> sys.stderr, " ack_received = %s" %ack_received
            local_ack_checksum = cal_Local_Checksum(ack_received)

            if(nextSeq < base + window_Size):
                server_socket.setblocking(0)
                pack = MakePacket_GBN(current_Index)
                sent = server_socket.sendto(pack, client_address)
                current_Index = current_Index + 1
                nextSeq = nextSeq + 1
                server_socket.setblocking(1)

        else:
            print >> sys.stderr , "inside else case"
                
def corrupt_Pack_no(n):
    packet_samples = [0]
    for i in range(1, No_Of_Packets, 1):
        packet_samples.insert(i,i)

    m = (No_Of_Packets * n ) / 100
    arr = random.sample(packet_samples, m)
    return arr

def ACK_PKT_Loss(client_address):
    for i in range(0, No_Of_Packets, 1):
        pack = MakePacket(i)
        server_socket.setblocking(0)
        sent = server_socket.sendto(pack, client_address)
        
        ready = select.select([server_socket], [], [], 0.001)
        sleep(0.7)
        try:
            recv_packet, client_address = server_socket.recvfrom(1041)
        except socket.error:
            print >> sys.stderr , "******************timer timed out for ack %s" %i
            recv_packet = 0
        
        if(recv_packet):
            '''print >> sys.stderr," data pkt %s is acknowledged before timeout" %i'''
            ack_received, chksum_received = deassembleACK_Packet(recv_packet)
            local_ack_checksum = cal_Local_Checksum(ack_received)
            expected_ack = cal_expected_ACK(i)
            if(expected_ack == ack_received):
                 if(local_ack_checksum != chksum_received):
                    print >> sys.stderr, "Need to retransmit"

        else: #timer timeout
            print >> sys.stderr , " data packet %s is not acknowledged" %i
            sent = server_socket.sendto(pack, client_address)
            print >> sys.stderr, "data packet %s is retransmitted" %i
            recv_packet, client_address = server_socket.recvfrom(1041)
            ack_received, chksum_received = deassembleACK_Packet(recv_packet)
            local_ack_checksum = cal_Local_Checksum(ack_received)
            expected_ack = cal_expected_ACK(i)            
            if(expected_ack == ack_received):
                if(local_ack_checksum == chksum_received):
                    print >> sys.stderr , "Packet %s is send to receiver without errors after retrasmission due to timeout" %i
                    
    server_socket.setblocking(1)  
    message = 'EOF'
    sent = server_socket.sendto(message, client_address)


def Data_PKT_Loss(client_address):
    arr = corrupt_Pack_no(10)
    print >> sys.stderr , "arr = %s" %arr

    for i in range (0, No_Of_Packets, 1):
        pack = MakePacket(i)
        server_socket.setblocking(0)      

        if(i in arr):
            print >> sys.stderr, "********************* drop pkt %s" %i
        else:
            sent = server_socket.sendto(pack, client_address)

        ready = select.select([server_socket], [], [], 0.01)
        sleep(0.5)
        try:
            recv_packet, client_address = server_socket.recvfrom(1041)
        except socket.error:
            print >> sys.stderr , "timer timed out for packet %s" %i
            recv_packet = 0
        
        if(recv_packet):
            '''print >> sys.stderr," data pkt %s is acknowledged before timeout" %i'''
            ack_received, chksum_received = deassembleACK_Packet(recv_packet)
            local_ack_checksum = cal_Local_Checksum(ack_received)

            expected_ack = cal_expected_ACK(i)
            if(expected_ack == ack_received):
                if(local_ack_checksum == chksum_received):
                    print >> sys.stderr , "Packet %s is send to receiver without errors" %i
                else:
                    print >> sys.stderr, " Need to retransmit"

        else: #timer timeout
            print >> sys.stderr , "data packet %s is not acknowledged, " %i
            sent = server_socket.sendto(pack, client_address)
            print >> sys.stderr, "retransmitting packet %s" %i
            recv_packet, client_address = server_socket.recvfrom(1041)
            ack_received, chksum_received = deassembleACK_Packet(recv_packet)
            local_ack_checksum = cal_Local_Checksum(ack_received)
           
            expected_ack = cal_expected_ACK(i)
            if(expected_ack == ack_received):
                if(local_ack_checksum == chksum_received):
                    print >> sys.stderr , "Packet %s is send to receiver without errors after retrasmission due to timeout" %i
                        
    message = 'EOF'
    sent = server_socket.sendto(message, client_address)
    server_socket.setblocking(1)

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

def MakePacket(packet_No):
    startPosition = packet_No * 1024
    endPosition = startPosition + 1024
    data = buffer[startPosition:endPosition]
    data = str(data)
    if(packet_No % 2 == 0):
        sq = '0'
    else:
        sq = '1'
    
    checksum = cal_Checksum(packet_No)
    checksum = str(checksum)

    packet = [data, checksum, sq]
    packet = ''.join(packet)
    return packet

def cal_Local_Checksum(msg):
    Local_checksum =''.join([bin(~0)[3:] if x == '0' else bin(~1)[4:] for x in msg])
    return Local_checksum

def deassembleACK_Packet(recv_packet):
    ack_received = recv_packet[0:16]
    ack_Checksum = recv_packet[16:33]
    return ack_received, ack_Checksum

            
def detect_Error_ACK(client_address):
    for i in range (0, No_Of_Packets, 1):
        pack = MakePacket(i)
        sent = server_socket.sendto(pack, client_address)
        recv_packet, client_address = server_socket.recvfrom(1041)
        ack_received, chksum_received = deassembleACK_Packet(recv_packet)
        
        local_ack_checksum = cal_Local_Checksum(ack_received)
        expected_ack = cal_expected_ACK(i)

        print >> sys.stderr, "ack_received = %s" %ack_received
        if((chksum_received == local_ack_checksum) & (expected_ack ==  ack_received)):
            print >> sys.stderr ," All Set !!!"
        else:
            print >> sys.stderr, "retransmitting pkt = %s" %i
            pack = MakePacket(i)
            sent = server_socket.sendto(pack, client_address)

            recv_packet, client_address = server_socket.recvfrom(1041)
            ack_received, chksum_received = deassembleACK_Packet(recv_packet)
            local_ack_checksum = cal_Local_Checksum(ack_received)
            
    message = 'EOF'
    sent = server_socket.sendto(message, client_address)


def No_Error(client_address):
    for i in range (0, No_Of_Packets, 1):
        pack = MakePacket(i)
        sent = server_socket.sendto(pack, client_address)
        recv_packet, client_address = server_socket.recvfrom(1041)

        ack_received, chksum_received = deassembleACK_Packet(recv_packet)
        local_ack_checksum = cal_Local_Checksum(ack_received)
       
        expected_ack = cal_expected_ACK(i)

        if(expected_ack == ack_received):
            if(local_ack_checksum == chksum_received):
                print >> sys.stderr , "Packet %s is send to receiver without errors" %i
            else:
                print >> sys.stderr, " Need to retransmit"

    message = 'EOF'
    sent = server_socket.sendto(message, client_address)
    

def Packet_with_Errors(client_address):
    arr = corrupt_Pack_no(10)
    print >> sys.stderr, " arr = %s" %arr
    for i in range (0, No_Of_Packets, 1):
        if(i in arr):
            pack = MakePacket(i)
            data = pack[0:1024]
            data = str(data)
            
            c1 = pack[1024:1040]
            c2 = c1[0:3] # select 1st 3 bits
            c3 =''.join([bin(~0)[3:] if x == '0' else bin(~1)[4:] for x in c2])#corrupt 3 bits
            c4 = c1[3:17] # remaining bits
            c5 = [c3, c4]
            c5 = ''.join(c5)

            print >> sys.stderr ,"corrupted packet no. = %s" %i
            
            corrupt_pack = [data, c5] #form a faulty packet
            corrupt_pack = ''.join(corrupt_pack)
            print >> sys.stderr ,"corrupted packet no. = %s" %i
            
            sent = server_socket.sendto(corrupt_pack, client_address)
            recv_packet, client_address = server_socket.recvfrom(1041)
            
            ack_received,chksum_received = deassembleACK_Packet(recv_packet)
            local_ack_checksum = cal_Local_Checksum(ack_received)
            expected_ack = cal_expected_ACK(i)

            if((chksum_received == local_ack_checksum) & (expected_ack == ack_received)):
                print >> sys.stderr, "no errors found"

            else:
                print >> sys.stderr , " Packet %s has bit errors, retransmitting now.." %i
                pack = MakePacket(i)
                sent = server_socket.sendto(pack, client_address)

                recv_packet, client_address = server_socket.recvfrom(1041)
                local_ack_checksum = cal_Local_Checksum(ack_received)

                ack_received1, chksum_received1 = deassembleACK_Packet(recv_packet)
                if(local_ack_checksum == ack_received1):
                    print >> sys.stderr , "Receiver has received retransmitted packet %s successfully" %i
                
        else:
            pack = MakePacket(i)
            sent = server_socket.sendto(pack, client_address)

            recv_packet, client_address = server_socket.recvfrom(1041)
            
            ack_received, chksum_received = deassembleACK_Packet(recv_packet)
            local_ack_checksum = cal_Local_Checksum(ack_received)
            expected_ack = cal_expected_ACK(i)

            if((chksum_received == local_ack_checksum) & (expected_ack == ack_received)):
                print >> sys.stderr, "Correctly received packet %s at receiver without errors" %i
                
    message = 'EOF'
    sent = server_socket.sendto(message, client_address)
      

print >> sys.stderr, ' \n********* Starting up on %s port %s *********' % server_address
server_socket.bind(server_address)

print >> sys.stderr, '\n Sender waiting to receive message'

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

    elif(data == '2'):
        Packet_with_Errors(client_address)
        print >> sys.stderr ,"End of Option 2"


    elif(data =='3'):
        detect_Error_ACK(client_address)
        print >> sys.stderr ,"End of Option 3 "

    elif(data == '4'):
        ACK_PKT_Loss(client_address)
        print >> sys.stderr ,"End of Option 4 "

    elif(data == '5'):
        Data_PKT_Loss(client_address)
        print >> sys.stderr ,"End of Option 5"

    elif(data == '6'):
        print >> sys.stderr, "Exiting now.."
        bClose = 1

    elif(data == '7'):
        print >> sys.stderr , " enter into option 7"
        GBN(client_address)
        print >> sys.stderr, "End of Option 7"

    else:
        msg = " Please enter correct option \n Type 1: Without bit errors \n \t Type 2: Bit errors \n \t Type 3: Errors in acknowledgement from receiver \n \t"
        sent = server_socket.sendto(message, client_address)
        data, client_address = server_socket.recvfrom(packet_size)
        
server_socket.close()
        
