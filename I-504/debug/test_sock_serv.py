import socket
import pickle

def testserv():
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind('/tmp/socket_test.sock')
    server.listen(5)


    client, addr = server.accept()
    print("connected")
    with client:
        while True:
            data = client.recv(4096)
            if not data:
                print("break")
                break
            print(data)
            print(data.decode("utf-8"))

    client.close()
