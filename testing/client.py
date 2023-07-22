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
    client_socket.close()


# Usage of testing:
# test_create_request(account_list = None, sym_list = None):
# account_list:[[account_id, balance], [account_id, balance]...]
# sym_list: [[sym, account_id, num], [sym, account_id, num]...]
###############################################################################################
# test_trans_request(account_id, order_list = None, query_list = None, cancel_list = None):
# order_list:[[sym, amount, limit], [sym, amount, limit]...]
# query_list: [trans_id, trans_id...]
# cancel_list: [trans_id, trans_id...]
if __name__ == "__main__":
    start_time = time.time()
    print("Part 1: create tag test")
    # 1 st part: only test create tag
    test_create_request()
    test_create_request([[0, 0]])  # only create account 0
    # only create symble for account 0
    test_create_request(None, [["AAAAA", 0, 10]])
    # create multiple symbles for account 0
    test_create_request(None, [["BBBBB", 0, 10], ["CCCCC", 0, 10]])
    # add amount of symble "BBBBB" for account 0
    test_create_request(None, [["BBBBB", 0, 10]])
    # create account 1 and create symble for account 1
    test_create_request([[1, 100]], [["BBBBB", 1, 10]])
    # create account 2 and create multiple symbles for account 2
    test_create_request([[2, 900]], [["BBBBB", 2, 10], [
                        "CCCCC", 2, 30], ["AAAAA", 2, 20]])
    test_create_request([[3, 100], [4, 400], [5, 500]]
                        )  # create multiple accounts
    # create account 6 and 7 and add amount of symble "AAAAA" for account 0
    test_create_request([[6, 600], [7, 700]], [["AAAAA", 0, 10]])
    # error cases for create tag:
    # invalid account 8 when creating sym
    test_create_request(None, [["AAAAA", 8, 10]])
    # ????????????????????????????
    # amount cannot be negative when creating sym
    test_create_request(None, [["AAAAA", 0, -10]])
    test_create_request([[0, 100]])  # account 0 already exist
    # balance cannot be negative when creating account
    test_create_request([[9, -100]])

    print("Part 2: trans tag test")
    # 2 nd part: test trans tag, starting from account 10
    # prepare for testing trans tag
    # account 10, balance 10000, sym X, num 10
    test_create_request([[10, 100000]], [["X", 10, 10]])
    # account 11, balance 20, sym X, num 10
    test_create_request([[11, 20]], [["X", 11, 10]])
    # account 12, balance 100000, sym X, num 10
    test_create_request([[12, 100000]], [["X", 12, 10]])

    print("Test 1")
    # error case 1: account balance must never become negative when trans (buy order: if insufficient funds are available, the order is rejected)
    # user 10 sell 1 X @ $150, 11 buy 1 X @ $200 (Order placement sequence: user 11, 10) --> user 11 has insufficient funds
    # rejected, response error
    test_trans_request(11, [["X", 1, 200]], None, None)
    test_trans_request(10, [["X", -1, 150]], None, None)  # trans_id 1
    test_trans_request(10, None, [1], None)
    # response error -- invalid trans_id
    test_trans_request(10, None, [0], None)
    # response error -- trans_id does not belong to account_id
    test_trans_request(11, None, [1], None)
    # response error -- trans_id does not belong to account_id and invalid trans_id
    test_trans_request(11, None, [0], None)

    # any short sale is also rejected when trans (sell order: if insufficient shares are available, the order is rejected)
    # user 10 sell 100 X @ $150, 12 buy 100 X @ $200 (Order placement sequence: user 12, 10) --> user 10 has insufficient shares
    test_trans_request(12, [["X", 100, 200]], None, None)  # trans_id 2
    # rejected, response error
    test_trans_request(10, [["X", -100, 150]], None, None)
    test_trans_request(12, None, [2], None)
    # response error -- invalid trans_id
    test_trans_request(10, None, [3], None)

    print("Test 2")
    # error case 2: account is invalid -- order
    test_trans_request(100, [["X", 2, 100]], None, None)

    print("Test 3")
    # error case 3: account is invalid -- query
    test_trans_request(100, None, [2], None)

    print("Test 4")
    # error case 4: account is invalid -- cancel
    test_trans_request(100, None, None, [2])

    test_trans_request(10, None, None, [1])  # cancel trans_id 1
    test_trans_request(12, None, None, [2])  # cancel trans_id 2

    print("Test 5")
    # test case 5: define the execution price to be the price of the order that was open first
    # 13 sell 100 Y @ $150, 14 sell 100 Y @ $180, 15 buy 100 Y @ $200, Order placement sequence: 14's, 13's , 15's => user 13 and 15 match, execution price=$150
    # account 13, balance 100000, sym Y, num 1000
    test_create_request([[13, 100000]], [["Y", 13, 1000]])
    # account 14, balance 100000, sym Y, num 1000
    test_create_request([[14, 100000]], [["Y", 14, 1000]])
    # account 15, balance 100000, sym Y, num 1000
    test_create_request([[15, 100000]], [["Y", 15, 1000]])
    test_trans_request(14, [["Y", -100, 180]], None, None)  # trans_id 3
    test_trans_request(13, [["Y", -100, 150]], None, None)  # trans_id 4
    test_trans_request(15, [["Y", 100, 200]], None, None)  # trans_id 5
    test_trans_request(14, None, [3], None)
    test_trans_request(13, None, [4], None)
    test_trans_request(15, None, [5], None)

    print("Test 6")
    # test case 6: Once an order is canceled, it MUST NOT match with any other orders and MUST NOT execute.
    # 16 sell 100 M @ $150, 17 buy 100 M @ $200 (order is 17, 16) => normal situation: match, price=200
    # account 16, balance 100000, sym M, num 1000
    test_create_request([[16, 100000]], [["M", 16, 1000]])
    # account 17, balance 100000, sym M, num 1000
    test_create_request([[17, 100000]], [["M", 17, 1000]])
    test_trans_request(17, [["M", 100, 200]], None, None)  # trans_id 6
    test_trans_request(17, None, None, [6])  # cancel trans_id 6
    test_trans_request(17, None, [6], None)  # only canceled order
    test_trans_request(16, [["M", -100, 150]], None,
                       None)  # trans_id 7 ==> no match

    print("Test 7")
    # test case 7: partially executed order
    # 18 buy 300 N @ $125, 19 buy 200 N @ $127, 20 sell 400 N @ $124 (order is 18, 19, 20)
    # => User 18 buy 200 N @ $125, 19 buy 200 N @ $127, 20 sell 200 N @ $125 and 200 N @ $127
    # account 18, balance 1000000, sym N, num 1000
    test_create_request([[18, 1000000]], [["N", 18, 1000]])
    # account 19, balance 1000000, sym N, num 1000
    test_create_request([[19, 1000000]], [["N", 19, 1000]])
    # account 20, balance 1000000, sym N, num 1000
    test_create_request([[20, 1000000]], [["N", 20, 1000]])
    test_trans_request(18, [["N", 300, 125]], None, None)  # trans_id 8
    test_trans_request(19, [["N", 200, 127]], None, None)  # trans_id 9
    test_trans_request(20, [["N", -400, 124]], None, None)  # trans_id 10
    # response 100 N open, 200 N executed
    test_trans_request(18, None, [8], None)
    test_trans_request(19, None, [9], None)
    test_trans_request(20, None, [10], None)

    print("Test 8")
    # test case 8: Matching an order may require splirng one order into parts, in which case the time/priority of the unfulfilled part remains the same as when the original order was created.
    # Now, 18 buy 100 N @ $125; Then, 21 buy 100 N @ $125; Then, 20 sell 50 N @ $124
    # => User 18 and 20 match, price=$125
    # account 21, balance 1000000, sym N, num 1000
    test_create_request([[21, 1000000]], [["N", 21, 1000]])
    test_trans_request(21, [["N", 100, 125]], None, None)  # trans_id 11
    test_trans_request(20, [["N", -50, 124]], None, None)  # trans_id 12
    # response 50 N open, 250 N executed
    test_trans_request(18, None, [8], None)
    test_trans_request(20, None, [12], None)  # response 50 N executed
    test_trans_request(21, None, [11], None)  # response 100 N open

    print("Test 9")
    # test case 9: When cancel: any part of the order which has already executed is unaffected.
    # cancel trans_id 7 => response 50 N canceled and 250 N executed
    test_trans_request(18, None, None, [8])

    print("Test 10")
    # test case 10: After trans, creating a new position in the buyer’s account
    # 22 sell 100 K @ $150, 23 buy 100 K @ $200 (assume that these 2 orders got matched, and order is 23, 22)
    # => match, price=200
    # account 22, balance 1000000, sym K, num 1000
    test_create_request([[22, 1000000]], [["K", 22, 1000]])
    test_create_request([[23, 1000000]], None)  # account 23, balance 1000000
    test_trans_request(23, [["K", 100, 200]], None, None)  # trans_id 13
    test_trans_request(22, [["K", -100, 150]], None, None)  # trans_id 14
    test_trans_request(23, None, [13], None)  # response 100 K executed
    test_trans_request(22, None, [14], None)  # response 100 K executed
    # ????????????????????????How to query position table to see the new position created in the buyer’s account??????????????????????????????

    print("Test 11")
    # test case 11: match when seller and buyer have same price and amount; Then, try to cancel trans
    # => match; cancel will response error
    # account 24, balance 1000000, sym J, num 1000
    test_create_request([[24, 1000000]], [["J", 24, 1000]])
    test_create_request([[25, 1000000]], None)  # account 25, balance 1000000
    test_trans_request(25, [["J", 10, 100]], None, None)  # trans_id 15
    test_trans_request(24, [["J", -10, 100]], None, None)  # trans_id 16
    test_trans_request(25, None, [15], None)  # response 10 J executed
    test_trans_request(24, None, [16], None)  # response 10 J executed
    test_trans_request(25, None, None, [15])  # response error
    test_trans_request(24, None, None, [16])  # response error

    print("Test 12")
    # test case 12: match when seller and buyer have same price and different amount; Then, try to cancel trans
    # => match; for sell order, cancel will response error; for buy order, cancel will not response error
    # account 26, balance 1000000, sym H, num 1000
    test_create_request([[26, 1000000]], [["H", 26, 1000]])
    test_create_request([[27, 1000000]], None)  # account 27, balance 1000000
    test_trans_request(27, [["H", 10, 100]], None, None)  # trans_id 17
    test_trans_request(26, [["H", -5, 100]], None, None)  # trans_id 18
    test_trans_request(27, None, [17], None)  # response 5 H executed, 5 open
    test_trans_request(26, None, [18], None)  # response 5 H executed
    test_trans_request(27, None, None, [17])  # response 5 canceled
    test_trans_request(26, None, None, [18])  # response error

    print("Test 13")
    # test case 13: match when different amount; Then, try to cancel trans
    # => match, price=100; for buy order, cancel will response error; for sell order, cancel will not response error
    # account 28, balance 1000000, sym G, num 1000
    test_create_request([[28, 1000000]], [["G", 28, 1000]])
    test_create_request([[29, 1000000]], None)  # account 29, balance 1000000
    test_trans_request(29, [["G", 5, 100]], None, None)  # trans_id 19
    test_trans_request(28, [["G", -10, 50]], None, None)  # trans_id 20
    test_trans_request(29, None, [19], None)  # response 5 H executed, 5 open
    test_trans_request(28, None, [20], None)  # response 5 H executed
    test_trans_request(29, None, None, [19])  # response 5 canceled
    test_trans_request(28, None, None, [20])  # response error

    print("Test 14")
    # test case 14: match when different amount; Then, try to cancel trans
    # => match, price=50; for sell order, cancel will response error; for buy order, cancel will not response error
    # account 31, balance 1000000, sym Q, num 1000
    test_create_request([[31, 1000000]], [["Q", 31, 1000]])
    test_create_request([[30, 1000000]], None)  # account 30, balance 1000000
    test_trans_request(31, [["Q", -5, 50]], None, None)  # trans_id 21
    test_trans_request(30, [["Q", 10, 100]], None, None)  # trans_id 22
    test_trans_request(31, None, [21], None)  # response 5 Q executed
    test_trans_request(30, None, [22], None)  # response 5 Q executed, 5 Q open
    test_trans_request(31, None, None, [21])  # response error
    test_trans_request(30, None, None, [22])  # response 5 canceled

    print("Test 15")
    # test case 15: do not match---sell price > buyer price
    # account 33, balance 1000000, sym OO, num 1000
    test_create_request([[33, 1000000]], [["OO", 33, 1000]])
    test_create_request([[32, 1000000]], None)  # account 32, balance 1000000
    test_trans_request(33, [["OO", -50, 100]], None, None)  # trans_id 23
    test_trans_request(32, [["OO", 10, 99.9]], None, None)  # trans_id 24
    test_trans_request(33, None, [23], None)
    test_trans_request(32, None, [24], None)
    test_trans_request(33, None, None, [23])
    test_trans_request(32, None, None, [24])

    print("Test 16")
    # test case 16: do not match---sell price > buyer price
    # account 34, balance 1000000, sym I, num 1000
    test_create_request([[34, 1000000]], [["I", 34, 1000]])
    test_create_request([[35, 1000000]], None)  # account 35, balance 1000000
    test_trans_request(35, [["I", 50, 99]], None, None)  # trans_id 25
    test_trans_request(34, [["I", -100, 100]], None, None)  # trans_id 26
    test_trans_request(35, None, [25], None)
    test_trans_request(34, None, [26], None)
    test_trans_request(35, None, None, [25])
    test_trans_request(34, None, None, [26])

    print("Test 17")
    # test case 17: two sell order match with one buy order; then cancel
    # account 36, balance 1000000, sym S, num 1000
    test_create_request([[36, 1000000]], [["S", 36, 1000]])
    # account 37, balance 1000000, sym S, num 1000
    test_create_request([[37, 1000000]], [["S", 37, 1000]])
    test_create_request([[38, 1000000]], None)  # account 38, balance 1000000
    test_trans_request(36, [["S", -5, 100]], None, None)  # trans_id 27
    test_trans_request(37, [["S", -5, 99]], None, None)  # trans_id 28
    test_trans_request(38, [["S", 10, 101]], None, None)  # trans_id 29
    test_trans_request(36, None, [27], None)
    test_trans_request(37, None, [28], None)
    test_trans_request(38, None, [29], None)
    test_trans_request(36, None, None, [27])  # response cancel error
    test_trans_request(37, None, None, [28])  # response cancel error
    test_trans_request(38, None, None, [29])  # response cancel error

    print("Test 18")
    # test case 18: two sell order match with one buy order and split one sell order
    # account 39, balance 1000000, sym F, num 1000
    test_create_request([[39, 1000000]], [["F", 39, 1000]])
    # account 40, balance 1000000, sym F, num 1000
    test_create_request([[40, 1000000]], [["F", 40, 1000]])
    test_create_request([[41, 1000000]], None)  # account 41, balance 1000000
    test_trans_request(39, [["F", -5, 100]], None, None)  # trans_id 30
    test_trans_request(40, [["F", -5, 99]], None, None)  # trans_id 31
    test_trans_request(41, [["F", 9, 101]], None, None)  # trans_id 32
    test_trans_request(39, None, [30], None)
    test_trans_request(40, None, [31], None)
    test_trans_request(41, None, [32], None)
    test_trans_request(39, None, None, [30])  # response cancel 1 F canceled
    test_trans_request(40, None, None, [31])  # response cancel error
    test_trans_request(41, None, None, [32])  # response cancel error

    print("Test 19")
    # test case 19: two buy order match with one sell order
    test_create_request([[42, 1000000]], None)  # account 39, balance 1000000
    test_create_request([[43, 1000000]], None)  # account 40, balance 1000000
    # account 44, balance 1000000, sym Z, num 1000
    test_create_request([[44, 1000000]], [["Z", 44, 1000]])
    test_trans_request(42, [["Z", 5, 100]], None, None)  # trans_id 33
    test_trans_request(43, [["Z", 5, 99]], None, None)  # trans_id 34
    test_trans_request(44, [["Z", -10, 98]], None, None)  # trans_id 35
    test_trans_request(42, None, [33], None)
    test_trans_request(43, None, [34], None)
    test_trans_request(44, None, [35], None)
    test_trans_request(42, None, None, [33])  # response cancel error
    test_trans_request(43, None, None, [34])  # response cancel error
    test_trans_request(44, None, None, [35])  # response cancel error

    print("Test 20")
    # test case 20: User sell symbol that they do not have
    # => response error
    test_trans_request(44, [["SSSSSSS", -10, 98]], None, None)

    print("Test 21")
    # test case 21: Test whether the final total balance and total sym amount are the sam as the original $ and amount or not:
    # account 45, balance 30, sym FinalTest, num 10
    test_create_request([[45, 30]], [["FinalTest", 45, 10]])
    # account 46, balance 30, sym FinalTest, num 10
    test_create_request([[46, 30]], [["FinalTest", 46, 10]])
    test_trans_request(45, [["FinalTest", 5, 2]], None, None)  # trans_id 36
    test_trans_request(46, [["FinalTest", -1, 5]], None, None)  # trans_id 37
    test_trans_request(46, [["FinalTest", -1, 4]], None, None)  # trans_id 38
    test_trans_request(45, [["FinalTest", 5, 3]], None, None)  # trans_id 39
    test_trans_request(46, [["FinalTest", -7, 1]], None, None)  # trans_id 40
    # => 40, 39, 36 match
    test_trans_request(45, None, None, [36])
    test_trans_request(45, [["FinalTest", 1, 5]], None, None)  # trans_id 41
    # =>38, 41 match
    test_trans_request(45, [["FinalTest", 1, 10]], None, None)  # trans_id 42
    # trans_id 45 => balance is not enough => rej
    test_trans_request(46, None, None, [37])
    test_trans_request(46, [["FinalTest", -5, 5]], None, None)
    # trans_id 46 => sym is not enough => rej

    end_time = time.time()
    elapsed_time = end_time-start_time
    print(f"Total time: {elapsed_time} seconds")


# need to test these situations:
# # trans: account is invalid
# # account balance must never become negative when trans (buy order: if insufficient funds are available, the order is rejected)
# # any short sale is also rejected when trans (sell order: if insufficient shares are available, the order is rejected)
# After trans--two cases: creating a new position in the buyer’s account/ add amount to this sym of buyer's account
# # define the execution price to be the price of the order that was open first
# # Once an order is canceled, it MUST NOT match with any other orders and MUST NOT execute.
# cancel and open is mutually exculsive
# Canceling a Buy order refunds the purchase price to the buyer’s account. Canceling a Sell order returns the shares to the seller’s account (sym amount).
# # partially executed order
# server MUST NOT reply with more than one open to a particular query/trans_id.
# time: be in seconds since the epoch
# # When cancel: any part of the order which has already executed is unaffected.
# # Matching an order may require splirng one order into parts, in which case the time/priority of the unfulfilled part remains the same as when the original order was created.
# # user sell the symbol that they did not have
# query and cancel: trans_id must belong to the account id
# order, query, cancel do togeter
