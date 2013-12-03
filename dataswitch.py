import pox.core
pox.core.initialize()
from pox.datapaths.switch import SoftwareSwitch
from pox.datapaths.switch import ofp_hello
from pox.openflow.util import make_type_to_unpacker_table

from pox.core import core

import logging
import socket
import select
from binascii import hexlify

HOST = socket.gethostname()
#HOST = '150.254.149.27'
PORT = 6633
SELECT_TIMEOUT = 15

logging.basicConfig(filename = "pox.log",
                        level    = logging.DEBUG,
                        format   = "%(levelname)s - %(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger("test")

#========================================================================================================
class Connection():
    
    def __init__(self):
        self.unpackers = make_type_to_unpacker_table()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        
    def serve(self):
        '''reads messages from TCP client socket and pass them to SoftwareSwitch until OF controller will close the connection'''
        try:
            while core.running:
                # Await a read event
                rlist, wlist, elist = select.select( [self.sock], [], [], SELECT_TIMEOUT)
                # Test for timeout
                if [rlist, wlist, elist] == [ [], [], [] ]:
                    print "Select timeout elapsed.\n"
                    continue
                # Loop through each socket in rlist, read and print the available data
                for sock in rlist:
                    msg = sock.recv(8192)
                print 'Message received', hexlify(msg)
                
                if msg == "":
                    print 'Shutting down.'
                    break
                    
                # OpenFlow parsing occurs here:
                ofp_type = ord(msg[1])
                packet_length = ord(msg[2]) << 8 | ord(msg[3])
                if packet_length > len(msg):
                    break
                new_offset, msg_obj = self.unpackers[ofp_type](msg, 0)
                print ' Decoded OF message is:\n', msg_obj
                self.on_message_received(self, msg_obj)
        finally:
            self.sock.close()
            
    def set_message_handler(self, handler):
        '''method used by SoftwareSwitch to register handler for incoming OF messages'''
        self.on_message_received = handler
        
    def send(self, msg):
        '''method used by SoftwareSwitch to send OF messages 
        to OF controller through existing client socket connection'''
        print 'OF message to send:\n', msg
        if type(msg) is not bytes:
            if hasattr(msg, 'pack'):
                msg = msg.pack()
        print ' Coded message is', hexlify(msg)
        self.sock.sendall(msg)
        
#========================================================================================================
if __name__ == "__main__":

    switch = SoftwareSwitch(dpid=1, name="sw1")
    conn = Connection()
    switch.set_connection(conn)
    switch.send_hello()
    conn.serve()
