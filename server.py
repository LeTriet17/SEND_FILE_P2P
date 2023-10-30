import socket
import threading
from hyper_parameter import *
import pickle
import sys

save_remove = None


class Server:
    def __init__(self, ip_host, port):
        self.ip_host = ip_host
        self.port = port

    def listen(self):
        self.server_side = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_side.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_side.bind((self.ip_host, self.port))

        self.sockets_list = [self.server_side]
        self.clients_banded = {}
        self.socket_addr_port = []
        self.id_peer = 1
        self.peer_list = []
        self.peer_file = {}
        print("Server is active:")
        self.server_side.listen(QUEUE_CLIENT)  # can modify this variable

    def server_message(self, obj_send):
        msg = pickle.dumps(obj_send)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        return msg

    def auth_message(self, client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode("utf-8").strip())
            return {"header": message_header, "data": client_socket.recv(message_length)}
        except:
            return False

    def check_auth(self, auth):
        for usr in list_user:
            flag = True
            if auth["user_name"] != usr["user_name"]:
                flag = False
            if auth["password"] != usr["password"]:
                flag = False
            if flag == True:
                return True
        return False

    def receive_message(self, client_socket):
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        message = client_socket.recv(message_length)

        return pickle.loads(message)

    def retrieve_info(self):
        for clients in self.socket_addr_port:
            print('Client: ' + str(clients[1]) + '| Port: '+str(clients[2]))

    def remove_client(self, sock_to_remove):
        for clients in self.socket_addr_port:
            if clients[0] is sock_to_remove:
                self.socket_addr_port.remove(clients)

    def getIpFromSocket(self, sock_to_rcv):
        for client in self.socket_addr_port:
            if client[0] is sock_to_rcv:
                return client[1]

    def conservation(self, client_socket):
        save_remove = None
        while True:
            try:
                message_user = self.receive_message(client_socket)
                print(message_user["type"])
                if message_user == False:
                    break
                
                elif message_user["type"] == CHAT_PROTOCOL_PUBLIC_FILE:
                    message_send = {"user_name": "Server",
                                    "type": CHAT_PROTOCOL_PUBLIC_FILE_ACK}
                    self.peer_file.setdefault(message_user["peer_name"], []).append(message_user["file_name"])
                elif message_user["type"] == CHAT_PROTOCOL_SEARCH_FILE:
                    message_send = {"user_name": "Server",
                                    "type": CHAT_PROTOCOL_SEARCH_FILE_ACK}
                    matching_peer = [peer_name for peer_name, file_list in self.peer_file.items() if message_user["file_name"] in file_list]
                    peer_list = [peer for peer in self.peer_list if peer[0] in matching_peer]
                    message_send["peer_list"] = peer_list
                    client_socket.send(self.server_message(message_send))
                elif message_user["type"] == CHAT_PROTOCOL_HI:
                    # ================message definition==================
                    message_send = {"user_name": "Server",
                                    "type": CHAT_PROTOCOL_HI_ACK}
                    message_send["id_peer"] = self.id_peer
                    message_send["ip"] = self.getIpFromSocket(client_socket)
                    message_send["port"] = message_user["port"]
                    message_send["peer_name"] = message_user["peer_name"]
                    self.peer_list.append(
                        [message_send["peer_name"], message_send["port"], message_send["ip"], message_send["id_peer"]])
                    save_remove = [message_send["peer_name"], message_send["port"],
                                   message_send["ip"], message_send["id_peer"]]
                    message_send["peer_list"] = self.peer_list
                    # =====================================================
                    client_socket.send(self.server_message(message_send))
                    self.id_peer += 1
                elif message_user["type"] == CHAT_PROTOCOL_BYE:
                    # ================message definition==================
                    message_send = {"user_name": "Server",
                                    "type": CHAT_PROTOCOL_BYE_ACK}
                    message_send["id_peer"] = message_user["id_peer"]
                    message_send["ip"] = self.getIpFromSocket(client_socket)
                    message_send["port"] = message_user["port"]
                    message_send["peer_name"] = message_user["peer_name"]
                    # =====================================================
                    self.peer_list.remove(
                        [message_send["peer_name"], message_send["port"], message_send["ip"], message_send["id_peer"]])
                    client_socket.send(self.server_message(message_send))
                    self.sockets_list.remove(client_socket)
                    self.remove_client(client_socket)
                    self.clients_banded[message_user["peer_name"]] = 0
                    client_socket.close()
                    return
            except:
                self.peer_list.remove(save_remove)
                self.sockets_list.remove(client_socket)
                self.remove_client(client_socket)
                client_socket.close()
                self.clients_banded[message_user["peer_name"]] = 0
                return

    def run(self):
        while True:
            try:
                client_socket, client_address = self.server_side.accept()

                # ============authentication process===================
                auth = self.auth_message(client_socket)
                if auth == False:
                    continue
                data_auth = pickle.loads(auth["data"])
                if data_auth["type"] != AUTHENTICATION:
                    continue
                num_ban = self.clients_banded.get(data_auth["user_name"], 0)
                if num_ban == ALREADY_CONNECT:
                    print("refuse connection!!! from {},{} with username because already connection: {}".format(
                        client_address[0], client_address[1], data_auth["user_name"]))
                    client_socket.send(
                        self.server_message(auth_already_connect))
                    continue
                if num_ban == FAIL_CONNECT:
                    print("refuse connection!!! from {},{} with username: {}".format(
                        client_address[0], client_address[1], data_auth["user_name"]))
                    client_socket.send(self.server_message(auth_fail_connect))
                    continue
                if self.check_auth(data_auth) == False:
                    # self.clients_banded[data_auth["user_name"]] = self.clients_banded.get(
                    #     data_auth["user_name"], 0) + 1
                    print("refuse connection!!! from {},{} with username: {}".format(
                        client_address[0], client_address[1], data_auth["user_name"]))
                    client_socket.send(self.server_message(auth_fail_connect))
                    continue
                # self.clients[data_auth["user_name"]] = 1
                client_socket.send(self.server_message(auth_success_connect))
                print("Connection from {} has been established!!!".format(
                    client_address))
                self.socket_addr_port.append(
                    [client_socket, client_address[0], client_address[1]])
                self.clients_banded[data_auth["user_name"]] = ALREADY_CONNECT
                # client_socket.setblocking(0)
                self.sockets_list.append(client_socket)
                t = threading.Thread(
                    target=self.conservation, args=(client_socket,))
                t.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

            except KeyboardInterrupt:
                print('\n\n\nShutdown Server....')
                for sock in self.sockets_list:
                    sock.close()
                sys.exit(0)


if __name__ == "__main__":
    #if len(sys.argv) < 2:
    #    print("Error: usage: ./" + sys.argv[0] + '<Port>')
    port = 5000
    server = Server('192.168.1.3', port)
    server.listen()
    server.run()
