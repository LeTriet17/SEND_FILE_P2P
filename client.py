import socket
from threading import *
from hyper_parameter import *
import pickle
import signal
import sys
from helper_function import *
import time
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,QStackedWidget,QGridLayout,QMessageBox,QFileDialog,QHBoxLayout,QComboBox
from PyQt6.QtCore import Qt
name = ""
password = ""
our_port = 3333
p2p_server_addr = ""   # IPv4 server
p2p_server_port = 5000   # Port server
ours_server = ""
my_ip_addr = socket.gethostbyname(socket.gethostname())
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# thread our_server
active_conn_sock = None
socket_peer = None
peer_list = []
my_id_peer = None
def processSignal(msg,signal):
    global chat_message
    global txt
    global entry
    global root

    global peer_list
    global my_id_peer
    global socket_peer_list
    global active_conn

    
    if signal == 'quit':
        message_request = {}
        message_request["type"] = CHAT_PROTOCOL_BYE
        message_request["peer_name"] = name
        message_request["port"] = our_port
        message_request["id_peer"] = my_id_peer
        server.send(send_client_message(message_request))

    if signal == 'connection':
        # print(msg)
        # to connect with someone
        global socket_peer
        peer_to_connect = msg[0]
        socket_peer = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        # 1 peer: out_port = destination_port
        print("peer_to_connect: ",
                peer_to_connect[2], 3333)
        # aka: port, hostname
        socket_peer.connect((peer_to_connect[2], 3333))
        print("connect with {} is established".format(
            peer_to_connect[0]))
        time.sleep(1)
        message_request = {}
        message_request["type"] = RECEIVE_FILE_PROTOCOL_CONNECT
        message_request["port"] = our_port
        message_request["ip_peer"] = my_ip_addr
        message_request["file_name"] = msg[1]
        socket_peer.send(send_client_message(message_request))

            
    if is_command(msg, 'dis_connection'):
        # to disconnect with someone
        aux_peer = []
        peer_to_dis = []
        id_to_dis = getPeerId(msg)
        if is_already_Connected(active_conn, id_to_dis):
            try:
                aux_peer = get_sockpeer_element(
                    active_conn_sock, id_to_dis)
                peer_to_dis = get_peer_element(active_conn, id_to_dis)
                print("disconnect with {}".format(peer_to_dis[0]))
                time.sleep(1)
                message_request = {}
                message_request["type"] = CHAT_PROTOCOL_DIS
                message_request["peer_name"] = name
                message_request["port"] = our_port
                message_request["ip_peer"] = my_ip_addr
                message_request["id_peer"] = my_id_peer
                aux_peer.send(send_client_message(message_request))
            except:
                print("id_peer: {} not found...".format(id_to_dis))
        else:
            print("id_peer: {} not found...".format(id_to_dis))

    else:
        pass

def connect_server(p2p_server_addr,user_name,password, out_port):
    global ours_server
    global server
    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # server``.settimeout(1.0)
        server.connect((p2p_server_addr, p2p_server_port))
    except:
        return False

    ours_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ours_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ours_server.bind(('', our_port))
    ours_server.listen(QUEUE_CLIENT)

    message = {}
    message["user_name"] = user_name
    message["password"] = password
    message["type"] = AUTHENTICATION

    server.send(send_client_message(message))

    print("wait to connect server")
    data_auth = get_client_data(server)

    if data_auth["user_name"] != "SERVER" or data_auth["type"] != AUTH_PROTOCOL_SUCCESS:
        server.close()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return False
    return True
def thread_server_listen():
    while True:
        try:
            data = get_client_data(server)
            print(data)
            if data:
                if data["type"] == CHAT_PROTOCOL_HI_ACK:
                    global peer_list,my_id_peer
                    peer_list = data["peer_list"]
                    my_id_peer = data["id_peer"]
                    print('Server:> the list of peers was received correctly, ' +
                          str(len(peer_list))+' total active peers')
                if data["type"] == CHAT_PROTOCOL_SEARCH_FILE_ACK:
                    peer_list = data["peer_list"]
                    print(f'Server:> Ip of peer {[peer[2] for peer in peer_list] if peer_list else []} was received correctly')
                if data["type"] == CHAT_PROTOCOL_BYE_ACK:
                    server.close()
                    print("Server:> Closing connections with server.......")
                    print('\n\nGoodbye '+name+'!\n')
                    input("Press Enter to continue...")
                    sys.exit(0)
                
                
            else:
                server.close()
                print("Goodbye!!!")
                break
        except Exception as error:
            print(f'Error: {error}')
            server.close()
            break
def thread_our_server_listen():
    while True:
        global active_conn_sock
        conn, addr = ours_server.accept()
        active_conn_sock = conn
        print('accept connection from {}'.format(active_conn_sock))
def thread_our_server_handle():
    while True:
        global active_conn_sock, socket_peer
        if active_conn_sock:
            data = get_client_data_time_out(active_conn_sock)
            if data["type"] == RECEIVE_FILE_PROTOCOL_CONNECT:
                message_send = {}
                message_send["type"] = RECEIVE_FILE_PROTOCOL_CONNECT_ACK
                print(data)
                with open(data["file_name"], 'rb') as file:
                    file_data = file.read()
                # Serialize the data
                serialized_data = pickle.dumps(file_data)
                message_send["data"] = serialized_data
                message_send["file_name"] = data["file_name"]
                active_conn_sock.send(send_client_message(message_send))
            if socket_peer:
                data = get_client_data_time_out(socket_peer)
                if data["type"] == RECEIVE_FILE_PROTOCOL_CONNECT_ACK:
                    file_data = file_data = pickle.loads(data["data"])
                    file_name = data["file_name"]
                    with open("{}/{}".format(name, file_name), 'wb') as f:
                        f.write(file_data)
                    #print("file {} transfer success from {} to {}!!".format(
                    #    file_name, data["peer_name"], name))

def get_client_data_time_out(server):
    try:
        header_length = server.recv(HEADER_LENGTH)
        message_length = int(header_length.decode("utf-8").strip())
        data_res = server.recv(message_length)
        data_res = pickle.loads(data_res)
    except Exception as error:
        print(f'Error: {error}')
        return False
    return data_res


class PageWindow(QtWidgets.QMainWindow):
    gotoSignal = QtCore.pyqtSignal(str)

    def goto(self, name):
        self.gotoSignal.emit(name)


class MainWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.UiComponents()

    def UiComponents(self):
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        self.setWindowTitle('Login Form')
        self.setGeometry(300, 250, 300, 250)
        vbox = QVBoxLayout()
        wid.setLayout(vbox)

        label = QLabel('Please enter details below')
        label.setStyleSheet('color: white; background-color: orange')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(label)

        self.username = QLineEdit()
        self.username.setPlaceholderText('Username')
        vbox.addWidget(self.username)

        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText('Password')
        self.pwd.setEchoMode(QLineEdit.EchoMode.Password)
        vbox.addWidget(self.pwd)

        self.port = QLineEdit()
        self.port.setPlaceholderText('Our Port')
        vbox.addWidget(self.port)

        self.IPv4 = QLineEdit()
        self.IPv4.setPlaceholderText('Server IPv4')
        vbox.addWidget(self.IPv4)

        self.messageLabel = QLabel('')
        self.messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(self.messageLabel)

        loginButton = QPushButton('Login')
        loginButton.clicked.connect(self.make_handleButton("loginButton"))
        vbox.addWidget(loginButton)

        self.setLayout(vbox)

    def make_handleButton(self, button):
        def handleButton():
            if button == "loginButton":
                if connect_server(self.IPv4.text(),self.username.text(), self.pwd.text(),self.port.text()):
                    global server
                    global name  
                    name = self.username.text()
                    message_first = {}
                    message_first["type"] = CHAT_PROTOCOL_HI
                    message_first["peer_name"] = self.username.text()
                    message_first["port"] = self.port.text()

                    server.send(send_client_message(message_first))
                    server_listen = Thread(target=thread_server_listen)
                    server_listen.start()

                    ours_server_listen = Thread(target=thread_our_server_listen)
                    ours_server_handle = Thread(target=thread_our_server_handle)

                    ours_server_listen.start()
                    ours_server_handle.start()
                    self.goto("search")
                else:
                    # If the connection to the server fails, show an error dialog
                    error_dialog = QMessageBox()
                    error_dialog.setWindowTitle("Connection Error")
                    error_dialog.setText("Could not connect to the server.")
                    error_dialog.exec()  # Show the dialog
        return handleButton


class SearchWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.left = 500
        self.top = 500
        self.width = 500
        self.height = 500
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Main Window")
        self.UiComponents()

    def goToMain(self):
        self.goto("main")

    def make_handleButton(self, button):
        def handleButton():
            if button == "btn1":
                self.goto("publicFile")
            elif button == "btn2":
                self.goto("receiveFile")
        return handleButton
    
    def UiComponents(self):
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        self.layout = QVBoxLayout()
        button_layout1 = QHBoxLayout()
        button_layout2 = QHBoxLayout()

        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.goToMain)
        button_layout1.addWidget(self.back_button,alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(button_layout1)

        wid.setLayout(self.layout)

        # button 1
        btn1 = QPushButton('Public File', self)
    #  btn1.setFont(QFont('Calibri', 20, QFont.Bold))
        btn1.setStyleSheet("border-width: 4px;")
        btn1.setToolTip('Public File')
        btn1.clicked.connect(self.make_handleButton("btn1"))
        button_layout2.addWidget(btn1)

        # button 2
        btn2 = QPushButton('Receive File', self)
    #  btn2.setFont(QFont('Calibri', 20, QFont.Bold))
        btn2.setStyleSheet("border-width: 4px;")
        btn2.setToolTip('Receive File')
        btn2.clicked.connect(self.make_handleButton("btn2"))
        button_layout2.addWidget(btn2)
        self.layout.addLayout(button_layout2)

        self.setLayout(self.layout)

        self.show()

    def closeEvent(self, event):
      close = QMessageBox.question(self,
                                    "QUIT",
                                    "Are you sure want to stop process?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
      if close == QMessageBox.StandardButton.Yes:
            event.accept()
      else:
         event.ignore()

class PublicFileWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.left = 500
        self.top = 500
        self.width = 500
        self.height = 500

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Public File")
        self.UiComponents()
    def goToSearch(self):
        self.goto("search")
    def UiComponents(self):
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        self.layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.goToSearch)
        button_layout.addWidget(self.back_button)

        self.select_file_button = QPushButton('Select File', self)
        self.select_file_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_file_button)

        self.layout.addLayout(button_layout)

        self.selected_file_label = QLabel("Selected File: ", self)
        self.layout.addWidget(self.selected_file_label)

        wid.setLayout(self.layout)
        

    def select_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file')
        if fname[0]:
            self.selected_file_label.setText("Selected File: " + os.path.basename(fname[0]))
            global server,name
            message_first = {}
            message_first["type"] = CHAT_PROTOCOL_PUBLIC_FILE
            message_first["peer_name"] = name
            message_first["file_name"] = os.path.basename(fname[0])

            server.send(send_client_message(message_first))


class ReceiveFileWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.left = 500
        self.top = 500
        self.width = 500
        self.height = 500
        self.peer_list = []  
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Receive File')
        self.UiComponents()
    def goToSearch(self):
        self.goto("search")
    def UiComponents(self):
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        self.layout = QVBoxLayout()
        #button_layout = QHBoxLayout()

        button_layout1 = QHBoxLayout()

        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.goToSearch)
        button_layout1.addWidget(self.back_button,alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(button_layout1)

        wid.setLayout(self.layout)
        #button_layout.addWidget(self.back_button)

        #self.start_button = QPushButton('Start', self)
        #self.start_button.clicked.connect(self.handle_start_session)
        #button_layout.addWidget(self.start_button)

        #self.layout.addLayout(button_layout)

        #self.stop_button = QPushButton('Stop', self)
        #self.stop_button.clicked.connect(self.handle_stop_session)
        #self.stop_button.setHidden(True)
        #self.layout.addWidget(self.stop_button)

        self.peer_combo = QComboBox(self)
        self.peer_combo.setHidden(True)
        self.layout.addWidget(self.peer_combo)

        self.select_peer_button = QPushButton('Select Peer', self)
        self.select_peer_button.clicked.connect(self.handle_select_session)
        self.select_peer_button.setHidden(True)
        self.layout.addWidget(self.select_peer_button)

        search_layout = QHBoxLayout()

        self.file_name = QLineEdit()
        self.file_name.setPlaceholderText('File Name')
        search_layout.addWidget(self.file_name)

        self.find_button = QPushButton('Find Peer', self)
        self.find_button.clicked.connect(self.find_file)
        self.find_button.clicked.connect(self.handle_find_session)
        search_layout.addWidget(self.find_button)

        self.layout.addLayout(search_layout)
        
        wid.setLayout(self.layout)
    def find_file(self):
        global server,peer_list
        message_first = {}
        message_first["type"] = CHAT_PROTOCOL_SEARCH_FILE
        message_first["file_name"] = self.file_name.text()
        peer_list = []
        server.send(send_client_message(message_first))
    def handle_find_session(self):
        self.peer_started = True
        time.sleep(1)
        peer_ip = [peer[2] for peer in peer_list]
        self.peer_combo.clear()    
        self.peer_combo.addItems(peer_ip)
        self.peer_combo.setHidden(False)
        self.select_peer_button.setHidden(False)

    def handle_select_session(self):
        for peer in peer_list:
            if peer[2] == self.peer_combo.currentText():
                self.peer_connect = peer
                break
        
        processSignal((self.peer_connect,self.file_name.text()),'connection')

    
    def send_file(self):
        if self.file_list:
            file_path = self.file_list[0]
            selected_peer = self.peer_combo.currentText()
            # Implement sending the file to the selected peer
        else:
            pass  # Show a message indicating that no file is selected

    def select_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file')
        if fname[0]:
            self.selected_file_label.setText("Selected File: " + fname[0])
class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.m_pages = {}

        self.register(MainWindow(), "main")
        self.register(SearchWindow(), "search")
        self.register(PublicFileWindow(), "publicFile")
        self.register(ReceiveFileWindow(), "receiveFile")

        self.goto("search")

    def register(self, widget, name):
        self.m_pages[name] = widget
        self.stacked_widget.addWidget(widget)
        if isinstance(widget, PageWindow):
            widget.gotoSignal.connect(self.goto)

    @QtCore.pyqtSlot(str)
    def goto(self, name):
        if name in self.m_pages:
            widget = self.m_pages[name]
            self.stacked_widget.setCurrentWidget(widget)
            self.setWindowTitle(widget.windowTitle())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())

        
