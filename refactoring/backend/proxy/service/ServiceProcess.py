from multiprocessing import Process, Value
from .ServiceClass import Service
from .stream import HTTPStream, TCPStream
from ..multiprocess import FilterBrokerAsker
from ..utils import block_packet, filter_packet, receive_from, start_tls, enable_ssl
from ..configuration.constants import HOST
import socket
import sys
import threading
import logging
import errno
import select
import signal
import os

class ServiceProcess(Process):

    def __init__(self, service : Service, asker : FilterBrokerAsker):
        super().__init__()
        self.service : Service = service
        self.asker : FilterBrokerAsker = asker

    @staticmethod
    def __get_address_family__(host : str = "::"):
        try:
            result = socket.getaddrinfo(host, 0, socket.AF_UNSPEC, socket.SOCK_STREAM)
            return result[0][0]
        except socket.gaierror as e:
            print(f"Error resolving host: {e}")
            return None
        
    def __exit__(signum, frame):
        with open(f"/tmp/{os.getpid()}", "w") as f:
            f.write(f"Received signal {signum} in process {os.getpid()}\n")
        sys.exit(0)
    
    def run(self):
        # this is the socket we will listen on for incoming connections
        proxy_socket = socket.socket(ServiceProcess.__get_address_family__(), socket.SOCK_STREAM)
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        signal.signal(signal.SIGTERM, ServiceProcess.__exit__)
        

        try:
            proxy_socket.bind(("::", self.service.port))
        except socket.error as e:
            print(e.strerror)
            sys.exit(5)
        proxy_socket.listen(100)


        try:
            
            while True:
                in_socket, in_addrinfo = proxy_socket.accept()
                logging.error(f'Connection from {in_addrinfo[0]},{in_addrinfo[1]}')
                proxy_thread = threading.Thread(target=ServiceProcess.connection_thread,
                                                args=(
                                                    self, in_socket
                                                ))
                proxy_thread.start()

        except KeyboardInterrupt:
            sys.exit(0)

    

    def connection_thread(self, local_socket: socket.socket):
        """This method is executed in a thread. It will relay data between the local
        host and the remote host, while letting modules work on the data before
        passing it on."""
        target_ip = HOST
        remote_socket = socket.socket(ServiceProcess.__get_address_family__(target_ip))

        try:
            remote_socket.connect((target_ip, self.service.port))
        except socket.error as serr:
            if serr.errno == errno.ECONNREFUSED:
                for s in [remote_socket, local_socket]:
                    s.close()
                return None
            elif serr.errno == errno.ETIMEDOUT:
                for s in [remote_socket, local_socket]:
                    s.close()
                return None
            else:
                for s in [remote_socket, local_socket]:
                    s.close()
                raise serr

        # This loop ends when no more data is received on either the local or the
        # remote socket
        if self.service.type == "http" or self.service.type == "https":
            stream = HTTPStream() 
        else:
            stream = TCPStream()

        connection_open = True
        while connection_open:
            ready_sockets, _, _ = select.select(
                [remote_socket, local_socket], [], [])

            for sock in ready_sockets:
                try:
                    peer = sock.getpeername()
                except socket.error as serr:
                    if serr.errno == errno.ENOTCONN:
                        for s in [remote_socket, local_socket]:
                            s.close()
                        connection_open = False
                        break
                    else:
                        raise serr

                try:
                    stream.set_current_message(receive_from(sock, "http" in self.service.type))
                except socket.error as serr:
                    remote_socket.close()
                    local_socket.close()
                    connection_open = False
                    break

                if sock == local_socket:
                    # going from client to service
                    if not len(stream.current_message):
                        remote_socket.close()
                        local_socket.close()
                        connection_open = False
                        break

                    attack = filter_packet(stream, None)
                    if not attack:
                        remote_socket.send(stream.current_message)
                else:
                    # going from service to client
                    if not len(stream.current_message):
                        remote_socket.close()
                        local_socket.close()
                        connection_open = False
                        break

                    attack = filter_packet(stream, None)
                    if not attack:
                        local_socket.send(stream.current_message)

                if attack:
                    block_answer = "£TEST" + self.service.name + " " + attack
                    block_packet(local_socket, ServiceProcess.__get_address_family__("::"), remote_socket, block_answer)
                    connection_open = False
                    break
