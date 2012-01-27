# pybluez library
import bluetooth

server_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
client_sockets = []

server_socket.bind(("",bluetooth.PORT_ANY))
port = server_socket.getsockname()[1]
uuid = "7674047E-6E47-4BF0-831F-209E3F9DD23F"

print "Listening for devices..."

# advertise service
server_socket.listen(1)
bluetooth.advertise_service( server_socket, "Validation Host",
    service_id = uuid,
    service_classes = [ uuid, bluetooth.SERIAL_PORT_CLASS ],
    profiles = [ bluetooth.SERIAL_PORT_PROFILE ],
)

# accept incoming connections
client_sock, client_info = server_socket.accept()
client_sockets.append(client_sock)
print "Accepted Connection from ", client_info
