import socket
import os
import threading, wave, pyaudio, time
import json
import ipaddress
import struct
from queue import Queue

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

BUFF_SIZE = 65536

# global start_stream

new_controller_port = 420
controller_manage_port_start = 421
new_speaker_port = 690
speaker_out_start_port = 691

class Subnet:
    subnet = ''
    controller = ('', 0)
    speaker = ('', 0)
    def __init__(self, subnet, controller, speaker):
        self.subnet = subnet
        self.controller = controller
        self.speaker = speaker
    
    def is_ready(self) -> bool:
        return self.subnet != '' and self.controller != ('', 0) and self.speaker != ('', 0)

subnets: list[Subnet] = []
curr_subnet: Subnet = Subnet('',('', 0),('', 0))

def new_controller_listen(start_stream):  
    controller_listening_addr = (host_ip, (new_controller_port))

    controller_listen = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    controller_listen.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    controller_listen.bind(controller_listening_addr)

    print('server listening at', controller_listening_addr)

    while True:
        controller_client_subnet,controller_client_addr = controller_listen.recvfrom(BUFF_SIZE)
        print('GOT connection from ', controller_client_addr, controller_client_subnet)
        if subnets:
            for i, subnet in enumerate(subnets):
                print(subnet.subnet, controller_client_subnet, subnet.controller, subnet.speaker)
                if subnet.subnet == controller_client_subnet:
                    print("subnet object completed", controller_client_addr)
                    subnets[i-1].controller = controller_client_addr
                    print(subnets[i-1].subnet, controller_client_subnet, subnets[i-1].controller, subnets[i-1].speaker)
                    # curr_subnet = subnet
                    print(subnets[0].controller)
                    if subnet.is_ready() and not start_stream.is_set():
                        print("toggling stream")
                        start_stream.set()
                        print("the value of subnets[i] is {}, {}, {}".format(subnets[i].subnet, subnets[i].controller, subnets[i].speaker))
                        print("the value of subnet is {}, {}, {}".format(subnet.subnet, subnet.controller, subnet.speaker))
                        curr_subnet = subnets[i-1]
                        print("the value of subnet is {}, {}, {}".format(curr_subnet.subnet, curr_subnet.controller, curr_subnet.speaker))
                else:
                    print("subnet object created", controller_client_addr)
                    subnets.append(Subnet(controller_client_subnet, (controller_client_addr[0], controller_client_addr[1]), ('', 0)))
                    print(subnets)
        else:
            print("subnet object created", controller_client_addr)
            subnets.append(Subnet(controller_client_subnet, (controller_client_addr[0], controller_client_addr[1]), ('', 0)))
            print(subnets)

def new_speaker_listen(start_stream):
    speaker_listening_addr = (host_ip, (new_speaker_port))

    speaker_listen = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    speaker_listen.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    speaker_listen.bind(speaker_listening_addr)


    print('server listening at',speaker_listening_addr)

    while True:
        speaker_client_subnet,speaker_client_addr = speaker_listen.recvfrom(BUFF_SIZE)
        print('GOT connection from ',speaker_client_addr,speaker_client_subnet)
        if subnets:
            for i, subnet in enumerate(subnets):
                print(subnet.subnet, speaker_client_subnet, subnet.controller, subnet.speaker)
                if subnet.subnet == speaker_client_subnet:
                    print("subnet object completed", speaker_client_addr)
                    # curr_subnet.speaker = speaker_client_addr
                    subnets[i-1].speaker = speaker_client_addr
                    print(subnets[i-1].subnet, speaker_client_subnet, subnets[i-1].controller, subnets[i-1].speaker)
                    if subnet.is_ready() and not start_stream.is_set():
                        print("toggling stream")
                        start_stream.set()
                        print("the value of subnets[i] is {}, {}, {}".format(subnets[i].subnet, subnets[i].controller, subnets[i].speaker))
                        print("the value of subnet is {}, {}, {}".format(subnet.subnet, subnet.controller, subnet.speaker))
                        curr_subnet = subnets[i-1]
                        print("the value of subnet is {}, {}, {}".format(curr_subnet.subnet, curr_subnet.controller, curr_subnet.speaker))
                else:
                    print("subnet object created", speaker_client_addr)
                    subnets.append(Subnet(speaker_client_subnet, ('', 0), (speaker_client_addr[0], speaker_client_addr[1])))
                    print(subnets)
        else:
            print("subnet object created", speaker_client_addr)
            subnets.append(Subnet(speaker_client_subnet, ('', 0), (speaker_client_addr[0], speaker_client_addr[1])))
            print(subnets)

def manage_stream():
    print("starting stream")
    # print("the value of curr_subnet is {}, {}, {}".format(curr_subnet.subnet, curr_subnet.controller, curr_subnet.speaker))
    print("the value of last subnet is {}, {}, {}".format(subnets[len(subnets) - 1].subnet, subnets[len(subnets) - 1].controller, subnets[len(subnets) - 1].speaker))
    curr_subnet = subnets[len(subnets) - 1]

    controller_listen_addr = (host_ip, (controller_manage_port_start))
    speaker_listen_addr = (host_ip, (speaker_out_start_port))

    controller_conn = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    controller_conn.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    controller_conn.bind(controller_listen_addr)
    
    speaker_conn = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    speaker_conn.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    speaker_conn.bind(speaker_listen_addr)

    CHUNK = 10*1024
    wf = wave.open("temp.wav")
    wf_duration = (wf.getnframes() / wf.getframerate())

    print(wf_duration)

    data = None
    sample_rate = wf.getframerate()

    while True:
        msg,_ = controller_conn.recvfrom(BUFF_SIZE)
        print(msg)
        match msg:
            case b'go':
                print(curr_subnet.controller)
                print(curr_subnet.speaker)
                controller_conn.sendto(b'playing', curr_subnet.controller)
                speaker_conn.sendto(struct.pack("f", wf_duration), curr_subnet.speaker)
                timer = time.perf_counter()
                while True:
                    if (time.perf_counter() - wf_duration) >= timer:
                        break
                    else:
                        data = wf.readframes(CHUNK)
                        speaker_conn.sendto(data, curr_subnet.speaker)
                        time.sleep(0.8*CHUNK/sample_rate)
                speaker_conn.sendto(b'stream complete', curr_subnet.speaker)
                controller_conn.sendto(b'stream complete', curr_subnet.controller)
            case b'exit':
                break
            case _:
                break

def main():
    start_stream = threading.Event()
    start_stream.clear()

    def check_subnet_storage():
        subnets_len = len(subnets)
        last_curr_subet_cache = curr_subnet
        print("subnet len is {}".format(subnets_len))
        # print("the subnet object at that index is {}, {}, {}".format(subnets[subnets_len].subnet, subnets[subnets_len].controller, subnets[subnets_len].speaker))
        # print("the value of curr_subnet is {}, {}, {}".format(curr_subnet.subnet, curr_subnet.controller, curr_subnet.speaker))
        while True:
            if subnets_len != len(subnets) or last_curr_subet_cache != curr_subnet:
                subnets_len = len(subnets)
                last_curr_subet_cache = curr_subnet
                print("subnet len is {}".format(subnets_len))
                print("the subnet object at that index is {}, {}, {}".format(subnets[subnets_len-1].subnet, subnets[subnets_len-1].controller, subnets[subnets_len-1].speaker))
                print("the value of curr_subnet is {}, {}, {}".format(curr_subnet.subnet, curr_subnet.controller, curr_subnet.speaker))
            
    check_subnet_storage_thread = threading.Thread(target=check_subnet_storage, args=())
    check_subnet_storage_thread.start()
    
    stream_thread = threading.Thread(target=manage_stream, args=())
    controller_listening_thread = threading.Thread(target=new_controller_listen, args=(start_stream, ))
    speaker_listening_thread = threading.Thread(target=new_speaker_listen, args=(start_stream, ))
    controller_listening_thread.start()
    speaker_listening_thread.start()

    while True:
        if start_stream.is_set():
            print("streaming thread starting")
            stream_thread.start()
            break
        
    
if __name__ == "__main__":
    main()