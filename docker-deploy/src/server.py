import socket
from db import *
from multiprocessing import Process
from multiprocessing import Pool
import multiprocessing
debug_print = False
l = multiprocessing.Lock()


def handle_request(xml_request, session):
    # Parse xml request: fromstring() parses XML from a string directly into an root Element
    root = ET.fromstring(xml_request)
    # response to user
    response = ET.Element('results')
    # begin to handle different kind of request: create and transactions
    # create:
    if root.tag == "create":
        for child in root:
            # symbol:
            if child.tag == "symbol":
                sym = child.attrib['sym']
                # insert position:
                for a_position in child:
                    if a_position.tag == "account":
                        account_id = a_position.attrib['id']
                        amount = a_position.text
                        insert_postion(session, account_id,
                                       sym, float(amount), response)
            # account:
            elif child.tag == "account":
                account_id = child.attrib['id']
                balance = float(child.attrib['balance'])
                insert_account(session, account_id, balance, response)
    # transactions:
    elif root.tag == "transactions":
        account_id = root.attrib["id"]
        account_valid = account_exists(session, account_id)
        for child in root:
            # first of all, handle the situation where this account ID is invalid
            # for order
            if child.tag == "order" and not account_valid:
                ET.SubElement(response, 'error', {
                              'sym': child.attrib["sym"], 'amount': child.attrib["amount"], 'limit': child.attrib["limit"]}).text = "Account ID is invalid"
                continue
            # for query or cancel
            if (child.tag == "query" or child.tag == "cancel") and not account_valid:
                trans_id = child.attrib["id"]
                ET.SubElement(response, 'error', {
                              'id': trans_id}).text = "Account ID is invalid"
                continue
            # order:
            if child.tag == "order":
                amount = float(child.attrib["amount"])
                sym = child.attrib["sym"]
                limit_price = float(child.attrib["limit"])
                if amount > 0:
                    insert_buy_order(session, account_id, amount,
                                     sym, limit_price, response)
                    match_and_execute(session, sym)
                elif amount < 0:  # I change this because amount=0 doesn't make sense
                    insert_sell_order(session, account_id,
                                      -amount, sym, limit_price, response)
                    match_and_execute(session, sym)
            elif child.tag == "query":
                trans_id = child.attrib["id"]
                query(session, account_id, trans_id, response)
            elif child.tag == "cancel":
                trans_id = child.attrib["id"]
                cancel(session, account_id, trans_id, response)
    if debug_print:
        print(ET.tostring(response))  # debug
    return response


def recv_len(client_socket):
    num = ""
    recv_req = (client_socket.recv(1)).decode('utf-8')
    while recv_req != "\n":
        num += recv_req
        recv_req = (client_socket.recv(1)).decode('utf-8')
    return int(num)

# Make sure that server will receive all data that was sent by the client, regardless of its size.
# Keep receiving and concatenating packets until there is no more data to receive.


def recv_req(client_socket, req_len):
    request = b""
    while len(request) < req_len:
        packet = client_socket.recv(req_len - len(request))
        if not packet:
            break
        request += packet
    # ???????????????????????????encode?????????????????????
    return request.decode('utf-8')


def process_one_connection(client_socket):
    try:
        # a new postgres connection should be created by multiprocessing.
        engine = connect_db()
        Session = sessionmaker(bind=engine)
        session = Session()
        # receive the length of the request from the client
        req_len = recv_len(client_socket)
        if req_len == 0:
            print("request cannot be empty")
            return
        # receive the request from the client
        request = recv_req(client_socket, req_len)
        xml_response = handle_request(request, session)
        response = ET.tostring(xml_response)
        # send response to client
        client_socket.send(response)
    except Exception as e:
        print(e)
    finally:  # this is for exception safety, if exception throws above, we can reach to this finally block and release the resources
        client_socket.close()
        session.close()
        engine.dispose()


def single_thread_process():
    init_db()
    # create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and port 12345
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', 12345))
    server_socket.listen(5)
    while True:
        # Establish connection with client.
        (client_socket, address) = server_socket.accept()
        process_one_connection(client_socket)


def process_per_request():
    init_db()
    # create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and port 12345
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', 12345))
    server_socket.listen(5)
    while True:
        # Establish connection with client.
        (client_socket, address) = server_socket.accept()
        # process per request
        p = Process(target=process_one_connection,
                    args=(client_socket,))
        p.start()


def pre_created_process():
    init_db()
    # create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and port 12345
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', 12345))
    server_socket.listen(5)  # maximum outstanding request.
    pool = Pool(processes=4)
    pool = multiprocessing.Pool(initializer=init_lock, initargs=(l,))
    while True:
        # Establish connection with client.
        (client_socket, address) = server_socket.accept()
        pool.apply_async(process_one_connection, (client_socket,))


def init_lock(l):
    global lock
    lock = l


if __name__ == "__main__":
    try:
        #single_thread_process()
        #process_per_request()
        pre_created_process()
    except Exception as e:# server start exception,like cannot connnect database..other exceptions are try catched when process one request.
        print(e)
