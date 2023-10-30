HEADER_LENGTH = 10
QUEUE_CLIENT = 5

CHAT_PROTOCOL_HI = 'Chat_Hi'
CHAT_PROTOCOL_HI_ACK = 'Chat_Hi_ACK'
CHAT_PROTOCOL_PUBLIC_FILE = 'Chat_Public_File'
CHAT_PROTOCOL_PUBLIC_FILE_ACK = 'Chat_Public_File_Ack'
CHAT_PROTOCOL_RECEIVE_FILE = 'Chat_Receive_File'
CHAT_PROTOCOL_RECEIVE_FILE_ACK = 'Chat_Receive_File_Ack'
CHAT_PROTOCOL_SEARCH_FILE = 'Chat_Search_File'
CHAT_PROTOCOL_SEARCH_FILE_ACK = 'Chat_Search_File_Ack'
CHAT_PROTOCOL_BYE = 'Chat_Bye'
CHAT_PROTOCOL_BYE_ACK = 'Chat_Bye_Ack'
RECEIVE_FILE_PROTOCOL_CONNECT = 'Receive_File_Connect'
RECEIVE_FILE_PROTOCOL_CONNECT_ACK = 'Receive_File_Connect_Ack'
AUTH_PROTOCOL_SUCCESS = 'Authentication_success'
AUTH_PROTOCOL_FAIL = 'Authentication_fail'
AUTH_PROTOCOL_ALREADY = 'Authentication_already'
AUTHENTICATION = 'Authentication'


ALREADY_CONNECT = 10
FAIL_CONNECT = 10

user1 = { "user_name": "1",
          "password": "123456"}

user2 = { "user_name": "2",
          "password": "123456" }
        
user3 = { "user_name": "3",
          "password": "123456"}

user4 = { "user_name": "4",
          "password": "123456"}

list_user = [user1,user2,user3,user4]

auth_success_connect = {
    "user_name" : "SERVER",
    "type" : AUTH_PROTOCOL_SUCCESS
}

auth_fail_connect = {
    "user_name" : "SERVER",
    "type" : AUTH_PROTOCOL_FAIL
}

auth_already_connect = {
    "user_name" : "SERVER",
    "type" : AUTH_PROTOCOL_ALREADY
}