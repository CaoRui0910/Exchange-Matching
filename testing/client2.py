import socket
import xml.etree.ElementTree as ET
import time
server_host = "vcm-32427.vm.duke.edu"  # change host here.
debug_print = True
# <create> contains 0 or more of the following children:
# <account id="ACCOUNT_ID" balance="BALANCE"/> and <symbol sym="SYM">
# <symbol sym="SYM"> can have one or more children which are <account id="ACCOUNT_ID"> NUM</account>
# Therefore, they can have None default value.
# example: test_create_request([[6, 600], [7, 700]], [["AAAAA", 0, 10]])
# account_list:[[account_id, balance], [account_id, balance]...]
# sym_list: [[sym, account_id, num], [sym, account_id, num]...]


def test_create_request(account_list=None, sym_list=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = server_host
    client_socket.connect((host, 12345))
    root = ET.Element("create")
    if account_list != None:
        for an_account in account_list:
            ET.SubElement(root, "account", {'id': str(
                an_account[0]), 'balance': str(an_account[1])})
    if sym_list != None:
        for a_sym in sym_list:
            request0 = ET.SubElement(root, "symbol", {'sym': str(a_sym[0])})
            ET.SubElement(request0, 'account', {
                          'id': str(a_sym[1])}).text = str(a_sym[2])
    str_request = ET.tostring(root, encoding='utf-8')
    request_len = len(str_request)
    client_socket.sendall(str(request_len).encode(
        'utf-8') + b'\n' + str_request)
    response = (client_socket.recv(9000)).decode('utf-8')
    if debug_print:
        print(response)
    client_socket.close()


if __name__ == "__main__":
    start_time = time.time()
    for i in range(100):
        test_create_request([[i, 1000000000]], [['x', i, 10]])
    end_time = time.time()
    elapsed_time = end_time-start_time
    print(f"Total time: {elapsed_time} seconds")
