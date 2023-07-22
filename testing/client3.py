import socket
import xml.etree.ElementTree as ET
import time
server_host = "vcm-32427.vm.duke.edu"  # change host here.
debug_print = False
# <create> contains 0 or more of the following children:
# <account id="ACCOUNT_ID" balance="BALANCE"/> and <symbol sym="SYM">
# <symbol sym="SYM"> can have one or more children which are <account id="ACCOUNT_ID"> NUM</account>
# Therefore, they can have None default value.
# example: test_create_request([[6, 600], [7, 700]], [["AAAAA", 0, 10]])
# account_list:[[account_id, balance], [account_id, balance]...]
# sym_list: [[sym, account_id, num], [sym, account_id, num]...]


def test_create_request(account_list=None, sym_list=None):
    # create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to the server
    host = server_host
    client_socket.connect((host, 12345))

    # generate xml create request using account_id, balance, and sym_dic:
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
    # ??????????????? encode request ?????????????????????????
    str_request = ET.tostring(root, encoding='utf-8')
    request_len = len(str_request)
    client_socket.sendall(str(request_len).encode(
        'utf-8') + b'\n' + str_request)

    # receive response from server
    # response = b""
    # while True:
    #     packet = client_socket.recv(4096)
    #     if not packet:
    #         break
    #     response += packet
    # ???????? receive all response ???????????
    response = (client_socket.recv(9000)).decode('utf-8')
    if debug_print:
        print(response)
    client_socket.close()


# <transactions> tag MUST have one or more children, each of which is an <order> tag, a <cancel> tag, or a <query> tag.
# <order sym="SYM" amount="AMT" limit="LMT"/>
# <query id="TRANS_ID">
# <cancel id="TRANS_ID">
# order_list:[[sym, amount, limit], [sym, amount, limit]...]
# query_list: [trans_id, trans_id...]
# cancel_list: [trans_id, trans_id...]
def test_trans_request(account_id, order_list=None, query_list=None, cancel_list=None):
    # create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to the server
    # ?????????????????????????
    host = server_host
    client_socket.connect((host, 12345))

    # generate xml transactions request using account_id, balance, and sym_dic:
    root = ET.Element("transactions", {'id': str(account_id)})
    if order_list != None:
        for an_order in order_list:
            ET.SubElement(root, "order", {'sym': str(an_order[0]), 'amount': str(
                an_order[1]), 'limit': str(an_order[2])})
    if query_list != None:
        for trans_id in query_list:
            ET.SubElement(root, "query", {'id': str(trans_id)})
    if cancel_list != None:
        for trans_id in cancel_list:
            ET.SubElement(root, "cancel", {'id': str(trans_id)})
    # ??????????????? encode request ?????????????????????????
    str_request = ET.tostring(root, encoding='utf-8')
    request_len = len(str_request)
    client_socket.sendall(str(request_len).encode(
        'utf-8') + b'\n' + str_request)

    # receive response from server
    # response = b""
    # while True:
    #     packet = client_socket.recv(4096)
    #     if not packet:
    #         break
    #     response += packet
    # ???????? receive all response ???????????
    response = (client_socket.recv(9000)).decode('utf-8')
    if debug_print:
        print(response)
    root = ET.fromstring(response)
    trans_id = 0
    for child in root:
        if child.tag == 'opened':
            trans_id = int(child.attrib['id'])
            break
    client_socket.close()
    return trans_id


if __name__ == "__main__":
    start_time = time.time()
    for i in range(100):
        # test_create_request([[i, 1000000000]], [['x', i, 10]])
        trans_id0 = test_trans_request(i, order_list=[['x', -5, i]])
        if trans_id0 != 0:
            test_trans_request(
                i, query_list=[trans_id0], cancel_list=[trans_id0])
        trans_id1 = test_trans_request(i, order_list=[['x', 5, i]])
        if trans_id1 != 0:
            test_trans_request(
                i, query_list=[trans_id1], cancel_list=[trans_id1])
    end_time = time.time()
    elapsed_time = end_time-start_time
    print(f"Total time: {elapsed_time} seconds")
