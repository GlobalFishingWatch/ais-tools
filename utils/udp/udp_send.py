import socket

# UDP_IP = "rpiais.local"
UDP_IP = "localhost"
UDP_PORT = 1234
MESSAGE = b"Hello, World!"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET,        # Internet
                     socket.SOCK_DGRAM)     # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
