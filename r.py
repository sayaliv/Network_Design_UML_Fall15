import socket
import sys
import os
import struct
from binascii import hexlify
import random

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 20660)
packet_size = 1024

buff = 1060
send_Packet = 1024
option_Selected = 0
packet_Count = -1
sq_previous = '0000000000000000'

print >> sys.stderr, '\n********* Starting Receiver *********'

def GBN():
    print >> sys.stderr," inside GBN"
    f_name = manage_FileNames()
    print >> sys.stderr ,"f_name = %s" %f_name  
    file = open(f_name, 'wb')

    data, server = client_socket.recvfrom(buff)
    i = 0
    while(data):
        if(data == 'EOF'):
            data = 0
            file.close()
        else:
            file_data = data[0:1024] #extract file data
            sum_calulated = cal_Checksum_for_received_data(file_data)#calculate sum of received data
            chksum_received = data[1024:1040]# checksum received from sender
            is_Success = add_Checksum(chksum_received, sum_calulated)
            sq_receive = data[1040:1055]
            sq_decimal = int(sq_receive, 2)
            print >> sys.stderr, "sq_decimal = %s" %sq_decimal
            if(packet_Count + 1 == sq_decimal):
                send_ack = sq_receive
                sq_previous = send_ack
            else:
                sq_previous = sq_previous
                send_ack = sq_previous
            if(is_Success == '1'):
                print >> sys.stderr , "checksum matched"
                file.write(file_data)
                chksum_ack = cal_Local_Checksum(send_ack)
                chksum_ack = str(chksum_ack)
                send_packet = [send_ack,chksum_ack]
                send_packet = ''.join(send_packet)
                sent = client_socket.sendto(send_packet, server_address)
                print >> sys.stderr, "packet %s is received correctly before timeout" %i
                data, server = client_socket.recvfrom(buff)
            else:
                print >> sys.stderr, "packet %s lost hecne ack won't be send" %i
        i = i + 1        

    
        
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

def corrupt_Pack_no(n):
    packet_samples = [0]
    for i in range(1, No_Of_Packets, 1):
        packet_samples.insert(i,i)

    m = (No_Of_Packets * n ) / 100
    arr = random.sample(packet_samples, m)
    return arr


def detect_Data_PKT_Loss():
    f_name = manage_FileNames()
    print >> sys.stderr ,"f_name = %s" %f_name  
    file = open(f_name, 'wb')
    
    data, server = client_socket.recvfrom(buff)
    i = 0
    while(data):
        i = i + 1
        if(data == 'EOF'):
            data = 0
            file.close()
        else:
            file_data = data[0:1024] #extract file data
            chksum_calulated = cal_Checksum_for_received_data(file_data)#calculate checksum of received data
            chksum_received = data[1024:1040]# checksum received from sender
            is_Success = add_Checksum(chksum_received, chksum_calulated)
            sq_receive = data[1040:1041]
            send_ack = 0
            if(sq_receive == '0'):
                send_ack = '0000000000000000'
            else:
                send_ack = '1111111111111111'
            if(is_Success == '1'):
                file.write(file_data)
                        
                chksum_ack = cal_Local_Checksum(send_ack)
                chksum_ack = str(chksum_ack)
                send_packet = [send_ack,chksum_ack]
                send_packet = ''.join(send_packet)
                sent = client_socket.sendto(send_packet, server_address)
                print >> sys.stderr, "packet %s is received correctly before timeout" %i
                data, server = client_socket.recvfrom(buff)
            else:
                print >> sys.stderr, "packet %s lost hecne ack won't be send" %i
                

def detect_ACK_PKT_Loss():
    f_name = manage_FileNames()
    print >> sys.stderr ,"f_name = %s" %f_name  
    file = open(f_name, 'wb')
    arr = corrupt_Pack_no(10)
    print >> sys.stderr , "arr = %s" %arr

    data, server = client_socket.recvfrom(buff)
    i = 0
    while(data):
        if(data == 'EOF'):
            data = 0
            file.close()
        else:
            if(i in arr):
                print >> sys.stderr, " ************ drop ack for packet %s" %i
            else:
                file_data = data[0:1024] # extract file data
                chksum_calulated = cal_Checksum_for_received_data(file_data)#calculate checksum of received data
                chksum_received = data[1024:1040]# checksum received from sender
                is_Success = add_Checksum(chksum_received, chksum_calulated)
                sq_receive = data[1040:1041]
                send_ack = 0
                if(sq_receive == '0'):
                    send_ack = '0000000000000000'
                else:
                    send_ack = '1111111111111111'
                if(is_Success == '1'):
                    file.write(file_data)
                        
                chksum_ack = cal_Local_Checksum(send_ack)
                chksum_ack = str(chksum_ack)
                send_packet = [send_ack,chksum_ack]
                send_packet = ''.join(send_packet)
                sent = client_socket.sendto(send_packet, server_address)
                '''print >> sys.stderr, "packet %s is received without any errors" %i'''
            data, server = client_socket.recvfrom(buff)

        i = i + 1

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

def detect_Bit_Errors():# This function is called when receiver selects Option = 2
    f_name = manage_FileNames()
    print >> sys.stderr ,"f_name = %s" %f_name  
    file = open(f_name, 'wb')
    
    data, server = client_socket.recvfrom(buff)
    i = 0
    while(data):
        if(data == 'EOF'):
            data = 0
            file.close()
        else:
            file_data = data[0:1024] # extract file data
            chksum_calulated = cal_Checksum_for_received_data(file_data)#calculate checksum of received data
            chksum_received = data[1024:1040]# checksum received from sender
            sq_received = data[1040:1041]
            
            is_Success = add_Checksum(chksum_received, chksum_calulated)
            print >> sys.stderr ,"chksum_received = %s" %chksum_received
            print >> sys.stderr ,"chksum_calulated = %s" %chksum_calulated
            if(is_Success == '1'):
                file.write(file_data)
                dupFlag = 0

                if(sq_received == '0'):
                    send_ack = '0000000000000000'
                else:
                    send_ack = '1111111111111111'
                
                chksum_ack = cal_Local_Checksum(send_ack)
                chksum_ack = str(chksum_ack)
                send_packet = [send_ack,chksum_ack]
                send_packet = ''.join(send_packet)
                sent = client_socket.sendto(send_packet, server_address)
                print >> sys.stderr, "packet %s is received without any errors" %i
            else:
                dupFlag = 1
                if(sq_received == '0'):
                    send_ack = '1111111111111111'
                else:
                    send_ack = '0000000000000000'
                chksum_ack = cal_Local_Checksum(send_ack)
                chksum_ack = str(chksum_ack)
                send_packet = [send_ack, chksum_received]
                send_packet = ''.join(send_packet)
                sent = client_socket.sendto(send_packet, server_address)
                
                
        if(dupFlag != 1):
            i = i + 1
        data, server = client_socket.recvfrom(buff)

def N0_Errors():# This function is called when receiver selects Option = 1
    f_name = manage_FileNames()
    print >> sys.stderr ,"f_name = %s" %f_name  
    file = open(f_name, 'wb')
    
    data, server = client_socket.recvfrom(buff)
    i = 0
    while(data):
        i = i + 1
        if(data == 'EOF'):
            data = 0
            file.close()
        else:
            file_data = data[0:1024] # extract file data
            chksum_calulated = cal_Checksum_for_received_data(file_data)#calculate checksum of received data
            chksum_received = data[1024:1040]# checksum received from sender
            is_Success = add_Checksum(chksum_received, chksum_calulated)
            sq_receive = data[1040:1041]
            send_ack = 0
            if(sq_receive == '0'):
                send_ack = '0000000000000000'
            else:
                send_ack = '1111111111111111'
            if(is_Success == '1'):
                file.write(file_data)
                        
                chksum_ack = cal_Local_Checksum(send_ack)
                chksum_ack = str(chksum_ack)
                send_packet = [send_ack,chksum_ack]
                send_packet = ''.join(send_packet)
                sent = client_socket.sendto(send_packet, server_address)
                print >> sys.stderr, "packet %s is received without any errors" %i
                data, server = client_socket.recvfrom(buff)

def error_ack():# This function is called when receiver selects Option = 3
    f_name = manage_FileNames()
    print >> sys.stderr ,"f_name = %s" %f_name  
    file = open(f_name, 'wb')
    
    data, server = client_socket.recvfrom(buff)
    
    i = 0
    m = 0
    prev_sq = 0
    arr = corrupt_Pack_no(10)
    print >> sys.stderr, "arr = %s" %arr
    while(data):
        if(data == 'EOF'):
            data = 0
            file.close()
        else:
            file_data = data[0:1024] # extract file data
            chksum_calulated = cal_Checksum_for_received_data(file_data)#calculate checksum of received data
            chksum_received = data[1024:1040]# checksum received from sender
            is_Success = add_Checksum(chksum_received, chksum_calulated)
            sq_received = data[1040:1041]

            if(is_Success == '1'):
                if( (m in arr) & (dupFlag != 1)):
                    if(sq_received == '0'):
                        send_ack = '0000000000000000'
                    else:
                        send_ack = '1111111111111111'

                    chksum_ack = cal_Local_Checksum(send_ack)
                    chksum_ack = str(chksum_ack)

                    print >> sys.stderr, "send_ack = %s" %send_ack
                
                    c1 = chksum_ack[1:4] # select 1st 3 bits
                    c2 =''.join([bin(~0)[3:] if x == '0' else bin(~1)[4:] for x in c1])#corrupt 3 bits
                    c3 = chksum_ack[3:17]
                    c4 = [c2,c3]
                    c4 = ''.join(c4)
                    send_packet = [send_ack,c4]
                    send_packet = ''.join(send_packet)
                    print >> sys.stderr ," %s has corrupted ACK" %m
                    sent = client_socket.sendto(send_packet, server_address)
                    dupFlag = 1
                    i = i -1
                    m = m -1
                else:
                    file_data = data[0:1024] # extract file data
                    chksum_calulated = cal_Checksum_for_received_data(file_data)#calculate checksum of received data
                    chksum_received = data[1024:1040]# checksum received from sender
                    is_Success = add_Checksum(chksum_received, chksum_calulated)
                    if(is_Success == '1'):
                        file.write(file_data)
                        if(sq_received == '0'):
                            send_ack = '0000000000000000'
                        else:
                            send_ack = '1111111111111111'
                        print >> sys.stderr, "send_ack = %s" %send_ack

                        chksum_ack = cal_Local_Checksum(send_ack)
                        chksum_ack = str(chksum_ack)
                        send_packet = [send_ack,chksum_ack]
                        send_packet = ''.join(send_packet)

                        sent = client_socket.sendto(send_packet, server_address)
                        print >> sys.stderr, "packet %s is received without any errors" %i
                        dupFlag = 0
                
       
                i = i + 1
                m = m + 1         
                data, server = client_socket.recvfrom(buff)
          
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

    elif(data == 'Option 2 Selected by receiver'):
        detect_Bit_Errors()

    elif(data == 'Option 3 Selected by receiver'):
        error_ack()
        
    elif(data == 'Option 4 Selected by receiver'):
        detect_ACK_PKT_Loss()

    elif(data == 'Option 5 Selected by receiver'):
        detect_Data_PKT_Loss()

    elif(data == 'Option 6 Selected by receiver'):
         bClose = 1

    elif(data == 'Option 7 Selected by receiver'):
        GBN()
        
client_socket.close()        
        
print >> sys.stderr, 'Receiver connection is closed'

