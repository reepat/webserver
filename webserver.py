import socket
import os
import argparse
import datetime
import sys

def parse_args():
    parser = argparse.ArgumentParser(description='Start a web server')
    parser.add_argument('-r', help= 'root directory for files', dest = 'OBJECT_DIR' , type=str ,default= 'object_dir/')
    parser.add_argument('-p', help= 'The port number on which the server will be listening for incoming connections', dest = 'PORT', type= int, default = 8001)
    args = parser.parse_args()
    return args
def get_content_type(file_name):
    if file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
        mime_type = 'image/jpg'
    elif file_name.endswith('.htm') or file_name.endswith('.html'):
        mime_type = 'text/html'
    else: mime_type = 'text/plain'
    return mime_type

def connect():
    args = parse_args()
    hoststr = socket.gethostname()
    HOST = socket.gethostbyname(hoststr)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, args.PORT))
    sock.listen(1)

    print('*****')
    print('port num: ', args.PORT)
    print('host: ', HOST)
    print('the server is ready to receive')
    print('*****')

    while True:
        conn, addr = sock.accept()
        try:
            message = conn.recv(4096).decode()
            print(message) #print request header
            fname = message.split()[1]
            file_type = get_content_type(fname)

            if file_type == 'image/jpg':

                path = args.OBJECT_DIR
                path = path[:-1]

                imgpath = path + fname
                f = open(imgpath, 'rb')
                out = f.read()
                f.close()
            else:
                f = open(fname[1:])
                out = f.read()

            #response header
            ok_msg = 'HTTP/1.1 200 OK\r\n'
            conn.sendall(ok_msg.encode())

            content_type = f'Content Type: {file_type}\r\n'
            conn.sendall(content_type.encode())

            content_length = f'Content Length: {len(out)}\r\n'
            conn.sendall(content_length.encode())

            date = datetime.datetime.now()
            date_str = date.strftime('%Y-%m-%d (%H:%M:%S.%f)\r\n\r\n')
            conn.sendall(date_str.encode())

            resp= content_type + content_length + date_str
            print(f'this is the response message:\n{ok_msg}{resp}')
            print('*****')
            #end response

            if file_type == 'image/jpg':
                conn.send(out)
            else:
                for i in range(0, len(out)):
                    conn.sendall(out[i].encode())
            conn.close()

        except IOError:
            not_found = 'HTTP/1.1 404 File Not Found\r\n\r\n'
            print('this is the response message:\n',not_found)
            conn.sendall(not_found.encode())
            conn.close()

    sock.close()  
        
if __name__ == "__main__":
    parse_args()
    connect()
    
