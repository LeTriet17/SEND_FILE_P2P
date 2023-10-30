import pickle
HEADER_LENGTH = 10


def get_peer_element(peer_list, my_peer_id):
    for peer in peer_list:
        if peer[3] == my_peer_id:
            return peer


def is_already_Connected(active_conn, id_peer):
    for conn in active_conn:
        if conn[3] is id_peer:
            return True
    return False


def get_sockpeer_element(active_conn_sock, id_to_find):
    for conn in active_conn_sock:
        if conn[0][3] is id_to_find:
            return conn[1]


def getPeerId(msg):
    try:
        return int(msg.split(' ')[1])
    except:
        return 0


def get_msg_to_send(msg, k=2):
    text_l = msg.split(' ')
    message = ''
    for i in range(k, len(text_l)):
        message = message + text_l[i]
        if i != len(text_l) - 1:
            message = message + ' '
    return message


def send_client_message(obj_message):
    msg = pickle.dumps(obj_message)
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    return msg


def get_client_data(server):
    header_length = server.recv(HEADER_LENGTH)
    message_length = int(header_length.decode("utf-8").strip())
    print('Message length: '+str(message_length))
    data_res = server.recv(message_length)
    data_res = pickle.loads(data_res)

    return data_res
