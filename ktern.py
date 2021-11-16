import os
os.add_dll_directory(os.getcwd())

from pyrfc import Connection,RFCLibError
import json
import sys
import decimal
import re
import base64

from constants import *
from cryptography.fernet import Fernet

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES

system_id = ''
function = ''


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj,bytes):
        return obj.decode(errors='ignore')
    raise TypeError




def process_json(request_json):
    #Check if the JSON emit is to add system or call bapi
    #else print the error message
    try:
        if request_json[EMIT] == ADD_SYSTEM:
            add_system(request_json)
        elif request_json[EMIT] == CALL_BAPI:
            call_bapi(request_json)
        else:
            print(json.dumps(general_exception(NOT_VALID_DATA)))
    except ValueError as e:
        print(json.dumps(general_exception(EMIT_KEY_NOT_FOUND)))


def add_system(request_json):
    try:
        #Get system id, ip, username, password, instance number and client
        system_id = request_json[ID]
        ip = request_json[IP]
        instance_number = request_json[INSTANCE_NUMBER]
        client = request_json[CLIENT]
        username = request_json[USERNAME]
        password = request_json[PASSWORD]
        #Check if the Credential and STFC_CONNECTION is available in the system
        #if yes create a system file with encrypted password in the system directory
        function = STFC_CONNECTION
        system = dict()
        system[ASHOST] = ip
        system[SYSNR] = instance_number
        system[CLIENT] = client
        system[USER] = username
        system[PASSWD] = password
        conn = Connection(**system)
        result = conn.call(STFC_CONNECTION, REQUTEXT=REQUTEXT)
        key = KTERN_CIPHER_TEXT.encode()
        fernet = Fernet(key)
        data = json.dumps(request_json).encode()
        encrypted = fernet.encrypt(data)
        system_file = SYSTEM_DIRECTORY + system_id + KTERN_EXTENSION
        with open(system_file, WRITE_BYTES) as file:
            file.write(encrypted)
        #Send Response as string from json which should have emit, flag, message etc 
        response = dict()
        response[EMIT] = ADD_SYSTEM_SUCCESS
        response[FLAG] = FLAG_SUCCESS
        response[SYSTEM] = system_id
        response[FUNCTION] = function
        response[ID] = system_id
        response[RESPONSE] = result
        print(json.dumps(response))
    except RFCLibError as e:
        print(json.dumps(get_rfc_lib_error(e,emit=ADD_SYSTEM_ERROR,system=system_id,function=function)))

    except FileNotFoundError as e:
        print(json.dumps(general_exception(SYSTEM_FILE_NOT_FOUND)))




def call_bapi(request_json):
    try:
        system_id = request_json[SYSTEM]
        function = request_json[FUNCTION]
        request_params = request_json[PARAMS]
        #Decrypt the system details using this system id from system directory
        key = KTERN_CIPHER_TEXT.encode()
        fernet = Fernet(key)
        system_file = SYSTEM_DIRECTORY + system_id + KTERN_EXTENSION
        with open(system_file, READ_BYTES) as file:
            data = file.read()
        system_detail = fernet.decrypt(data)
        system_detail = json.loads(system_detail.decode())
        system = dict()
        system[ASHOST] = system_detail[IP]
        system[SYSNR] = system_detail[INSTANCE_NUMBER]
        system[CLIENT] = system_detail[CLIENT]
        system[USER] = system_detail[USERNAME]
        system[PASSWD] = system_detail[PASSWORD]
        conn = Connection(**system)
        params = dict()
        for request_param in request_params:
            flag = request_param[FLAG]
            key = request_param[KEY]
            value = request_param[VALUE]
            if flag == 0:
                #String Parameter
                params[key] = value
            elif flag == 1:
                #Struct Parameter
                params[key] = value
                pass
            elif flag == 2:
                #Table parameter
                params[key] = value
        result = conn.call(function,**params)
        response = dict()
        response[EMIT] = BAPI_RESPONSE
        response[FLAG] = FLAG_SUCCESS
        response[SYSTEM] = system_id
        response[FUNCTION] = function
        response[ID] = system_id
        response[RESPONSE] = result
        print(json.dumps(response,default=decimal_default))
    except RFCLibError as e:
        print(json.dumps(get_rfc_lib_error(e,emit=BAPI_RESPONSE,system=system_id,function=function)))
    except FileNotFoundError as e:
        print(json.dumps(general_exception(SYSTEM_FILE_NOT_FOUND)))



def general_exception(e):
    error_string = str(e)
    exception = dict()
    exception[FLAG] = FLAG_GENERAL_EXCEPTION
    exception[ERROR] = error_string
    return exception


def get_rfc_lib_error(e,emit='',system='',function=''):
    error = dict()
    error[EMIT] = emit
    error[SYSTEM] = system
    error[FUNCTION] = function
    if e.code == RFC_COMMUNICATION_FAILURE:
        error[FLAG] = FLAG_ERROR_COMMUNICATION
    elif e.code == RFC_LOGON_FAILURE:
        error[FLAG] = FLAG_LOGON_FAILURE
    elif e.code == RFC_TIMEOUT:
        error[FLAG] = FLAG_TIMEOUT
    elif e.code == RFC_ABAP_EXCEPTION:
        if e.key == TABLE_NOT_AVAILABLE:
            error[FLAG] = FLAG_TABLE_NOT_AVAILABLE
        if e.key == FU_NOT_FOUND:
            error[FLAG] = FLAG_FUNCTION_NOT_FOUND
        if e.key == DATA_BUFFER_EXCEEDED:
            error[FLAG] = FLAG_DATA_BUFFER_EXCEEDED
    elif e.code == RFC_AUTHORIZATION_FAILURE:
        error[FLAG] = FLAG_AUTHORIZATION_FAILURE
    elif e.code == RFC_INVALID_PARAMETER:
        error[FLAG] = FLAG_FIELD_NOT_FOUND
    else:
        error[FLAG] = FLAG_GENERAL_EXCEPTION
    error[ERROR] = e.message
    return error


    
def decrypt(text_to_decrypt):
    try:
        backend = default_backend()
        salt = bytes(SALT_BYTES)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA1(),length=48,salt=salt,iterations=1000,backend=backend)
        key_bytes = kdf.derive(bytes(KTERN_CIPHER_TEXT, UTF_FORMAT))
        key = key_bytes[0:32]
        iv = key_bytes[32:]
        cipherbytes = base64.b64decode(text_to_decrypt)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        text_to_decrypt = cipher.decrypt(cipherbytes).decode(UTF_FORMAT).strip()
        return text_to_decrypt
    except Exception as e:
        print(e)

#Entry Point
if __name__=="__main__":

    #Create system directory if id dosen't exists
    if not os.path.exists(SYSTEM_DIRECTORY):
        os.makedirs(SYSTEM_DIRECTORY)

    #Create json directory if id dosen't exists
    if not os.path.exists(JSON_DIRECTORY):
        os.makedirs(JSON_DIRECTORY)

    #Chek the command line argument has atleast one parameter
    #If not print the error message
    #If yes; then check whether it's a valid json

    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        try:
            json_file_path = JSON_DIRECTORY + file_name
            # json_file_path = './' + file_name
            f = open(json_file_path, FILE_READ_MODE)
            request_json_string = f.read()
            f.close()
            #At this point request_json_string from the file has encrypted text 
            #We need to decrypt using the cipher text
            #request_json_string = decrypt(request_json_string) #Commenting Decryption
            request_json = json.loads(request_json_string)
            process_json(request_json)
        except FileNotFoundError as e:
            print(json.dumps(general_exception(JSON_FILE_NOT_FOUND)))
        except ValueError as e:
            print(json.dumps(general_exception(PARAMETER_IS_NOT_JSON)))
            print(str(e))
    else:
        print(json.dumps(general_exception(EXPECTS_ATLEAST_ONE_PARAMETER)))



