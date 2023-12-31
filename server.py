import socket
import os
import threading, wave, time
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

    while True:
        msg,_ = controller_conn.recvfrom(BUFF_SIZE)
        command = msg.decode("utf-8").split()
        print(command)
        stream_thread = threading.Thread(target=stream, args=(curr_subnet, controller_conn, speaker_conn, ))
        match command[0]:
            case 'play':
                if len(command) > 1:
                    match command[1]:
                        case 'crab_rave':
                            with song_name.mutex:
                                song_name.queue.clear()
                            song_name.put("crab_rave")
                            stream_thread.start()
                        case 'megalovania':
                            with song_name.mutex:
                                song_name.queue.clear()
                            song_name.put("megalovania")
                            stream_thread.start()
                        case _:
                            with song_name.mutex:
                                song_name.queue.clear()
                            song_name.put("crab_rave")
                            stream_thread.start()
                else:
                    with song_name.mutex:
                        song_name.queue.clear()
                    song_name.put("crab_rave")
                    stream_thread.start()
            case 'stop':
                print(run_stream.qsize())
                run_stream.put("stop")
                print(run_stream.qsize())
            case 'exit':
                break
            case _:
                break


def kill_at_song_finish(song):
    duration = (song.getnframes() / song.getframerate())
    print(duration)
    timer = time.perf_counter() + duration
    while True:
        if time.perf_counter() > timer:
            break
    run_stream.put("stop")

def stream(curr_subnet, controller_conn, speaker_conn):
    working_dir = os.getcwd()
    song_file_name = song_name.get()
    print(f"opening wav file at {working_dir}\\songs\\{song_file_name}.wav")
    with wave.open(f"{working_dir}\\songs\\{song_file_name}.wav", "rb") as song:
        print(curr_subnet.controller)
        print(curr_subnet.speaker)
        controller_conn.sendto(b'playing', curr_subnet.controller)
        # speaker_conn.sendto(struct.pack("f", song_duration), curr_subnet.speaker)

        timer_thread = threading.Thread(target=kill_at_song_finish, args=(song, ))
        timer_thread.start()

        CHUNK = 12 * 1024

        while run_stream.empty():
            data = song.readframes(CHUNK)
            if data != b'':
                speaker_conn.sendto(data, curr_subnet.speaker)
        
        speaker_conn.sendto(b'stop', curr_subnet.speaker)
        controller_conn.sendto(b'stream complete', curr_subnet.controller)
        print("stream complete")
        with run_stream.mutex:
            run_stream.queue.clear()
        print(run_stream.qsize())
        song.close()

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

def main():
    start_stream = threading.Event()
    start_stream.clear()
            
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
    run_stream = Queue()
    song_name = Queue()
    main()