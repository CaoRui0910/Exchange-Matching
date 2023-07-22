import time
import xml.etree.ElementTree as ET
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from orm_relations import *
from db_functions import *
from server import handle_request


def test_insert_account(session):
    # test insert_account() and account_exists()
    response = ET.Element('results')
    insert_account(session, 1234, -1, response)
    response_str = ET.tostring(response)
    print(response_str)
    print('\n')

    response = ET.Element('results')
    insert_account(session, 1234, 5000.5, response)
    response_str = ET.tostring(response)
    print(response_str)
    print('\n')

    response = ET.Element('results')
    insert_account(session, 1234, 500, response)
    print(ET.tostring(response))
    print('\n')

    response = ET.Element('results')
    insert_account(session, 5555, 500, response)
    print(ET.tostring(response))
    print('\n')

    response = ET.Element('results')
    insert_account(session, 5555, 0, response)
    print(ET.tostring(response))
    print('\n')

    show_all_accounts(session)
    print('\n')

# insert_postion()


def test_insert_position(session):
    response = ET.Element('results')
    insert_postion(session, 3333, "Tesla", 500.2, response)
    print(ET.tostring(response))
    print('\n')

    response = ET.Element('results')
    insert_postion(session, 1234, "Tesla", 500, response)
    print(ET.tostring(response))
    print('\n')

    response = ET.Element('results')
    insert_postion(session, 1234, "Tesla", 500, response)
    print(ET.tostring(response))
    print('\n')

    response = ET.Element('results')
    insert_postion(session, 1234, "Google", 500, response)
    print(ET.tostring(response))
    print('\n')

    response = ET.Element('results')
    insert_postion(session, 1234, "Tesla", -100, response)
    print(ET.tostring(response))
    print('\n')

    response = ET.Element('results')
    insert_postion(session, 5555, "Tesla", 499.8, response)
    print(ET.tostring(response))
    print('\n')

    show_all_positions(session)
    print('\n')

# insert buy_order


def test_insert_buy_sell(session):
    response = ET.Element('results')
    insert_buy_order(session, 1234, 100, "Tesla", 10, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_buyOrders(session)
    print('\n')

    response = ET.Element('results')
    insert_buy_order(session, 1234, 50, "Tesla", 5, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_buyOrders(session)
    print('\n')

    response = ET.Element('results')
    insert_buy_order(session, 1234, 1000, "Tesla", 20, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_buyOrders(session)
    print('\n')

    response = ET.Element('results')
    insert_buy_order(session, 1234, 3000.5, "Tesla", 1, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_buyOrders(session)
    print('\n')

    show_all_positions(session)

    response = ET.Element('results')
    insert_buy_order(session, 5555, 1, "Tesla", 5, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_buyOrders(session)
    print('\n')

    show_all_positions(session)

    # insert sell orders
    response = ET.Element('results')
    insert_sell_order(session, 1234, 300, "Google", 1, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_positions(session)
    show_all_sellOrders(session)
    print('\n')

    response = ET.Element('results')
    insert_sell_order(session, 5555, 300, "Google", 2, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_positions(session)
    show_all_sellOrders(session)
    print('\n')

    response = ET.Element('results')
    insert_sell_order(session, 1234, 999, "Tesla", 3, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_positions(session)
    show_all_sellOrders(session)
    print('\n')

    response = ET.Element('results')
    insert_sell_order(session, 1234, 1, "Tesla", 4, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_positions(session)
    show_all_sellOrders(session)
    print('\n')

    response = ET.Element('results')
    insert_sell_order(session, 1234, 1, "Tesla", 5, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_positions(session)
    show_all_sellOrders(session)
    print('\n')

    response = ET.Element('results')
    insert_sell_order(session, 5555, 1, "Tesla", 6, response)
    print(ET.tostring(response))
    show_all_accounts(session)
    show_all_positions(session)
    show_all_sellOrders(session)
    print('\n')


def create_match_suite1(session):
    response = ET.Element('testing')
    insert_account(session, account_id="123",
                   balance=10000000, response=response)
    insert_account(session, account_id="456",
                   balance=10000000, response=response)
    insert_postion(session, account_id="123", sym="X",
                   amount=100000, response=response)
    insert_sell_order(session, account_id="123", amount=200,
                      sym="X", limit_price=140, response=response)
    time.sleep(2)
    insert_sell_order(session, account_id="123", amount=200,
                      sym="X", limit_price=140, response=response)
    insert_sell_order(session, account_id="123", amount=100,
                      sym="X", limit_price=130, response=response)
    insert_sell_order(session, account_id="123", amount=500,
                      sym="X", limit_price=128, response=response)
    insert_buy_order(session, account_id="456", amount=200,
                     sym="X", limit_price=127, response=response)
    insert_buy_order(session, account_id="456", amount=300,
                     sym="X", limit_price=125, response=response)
    insert_buy_order(session, account_id="456", amount=300,
                     sym="X", limit_price=123, response=response)
    time.sleep(1)
    insert_buy_order(session, account_id="456", amount=200,
                     sym="X", limit_price=125, response=response)
    insert_sell_order(session, account_id="123", amount=400,
                      sym="X", limit_price=124, response=response)


def create_match_suite2(session):
    response = ET.Element('testing')
    insert_account(session, account_id="123",
                   balance=10000000, response=response)
    insert_account(session, account_id="456",
                   balance=10000000, response=response)
    insert_postion(session, account_id="123", sym="X",
                   amount=100000, response=response)
    insert_sell_order(session, account_id="123", amount=200,
                      sym="X", limit_price=10, response=response)
    time.sleep(2)
    insert_sell_order(session, account_id="123", amount=200,
                      sym="X", limit_price=20, response=response)
    insert_sell_order(session, account_id="123", amount=100,
                      sym="X", limit_price=30, response=response)
    insert_sell_order(session, account_id="123", amount=500,
                      sym="X", limit_price=30, response=response)
    insert_buy_order(session, account_id="456", amount=200,
                     sym="X", limit_price=127, response=response)
    insert_buy_order(session, account_id="456", amount=300,
                     sym="X", limit_price=125, response=response)
    insert_buy_order(session, account_id="456", amount=300,
                     sym="X", limit_price=123, response=response)
    time.sleep(1)
    insert_buy_order(session, account_id="456", amount=200,
                     sym="X", limit_price=125, response=response)
    insert_sell_order(session, account_id="123", amount=400,
                      sym="X", limit_price=124, response=response)
    # insert_buy_order(session, account_id="456", amount=200,
    #                 sym="X", limit_price=125, response=response)


def test_match_query_cancel(session):
    # create_match_suite2(session)
    create_match_suite1(session)
    print("before match:\n")
    show_all(session)

    match_and_execute(session, "X")
    print("after match:\n")
    show_all(session)
    response = ET.Element('results')
    query(session, 456, 8, response)
    print('\n')
    print(ET.tostring(response))
    response = ET.Element('results')
    cancel(session, 456, 6, response)
    cancel(session, 123, 2, response)
    print(ET.tostring(response))
    print("after cancel:\n")
    show_all(session)
    response = ET.Element('results')
    query(session, 456, 6, response)
    print(ET.tostring(response))
    show_all(session)


def show_all(session):
    show_all_sellOrders(session)
    show_all_buyOrders(session)
    show_all_accounts(session)
    show_all_positions(session)
    show_all_executed(session)
    show_all_cancelled(session)


def test_handle_request1(session):
    xml_request = ET.Element('create')
    ET.SubElement(xml_request, 'account', {
                  'id': str(1), 'balance': str(666666)})
    sys_et = ET.SubElement(xml_request, 'symbol', {'sym': 'Google'})
    ET.SubElement(sys_et, 'account', {'id': str(1)}).text = '5000'
    request_str = ET.tostring(xml_request)
    handle_request(request_str, session)
    show_all(session)


def test_handle_request2(session):
    create_match_suite1(session)
    match_and_execute(session, 'X')
    show_all(session)
    xml_request = "<transactions id='123'><order sym='Y' amount='200' limit='30.5'/><query id='3'/><cancel id='4'/></transactions>"
    handle_request(xml_request, session)
    show_all(session)


if __name__ == "__main__":
    engine = create_engine(
        'postgresql+psycopg2://postgres:passw0rd@localhost/stock', echo=False)

    Base.metadata.drop_all(engine)  # drop all created tables
    print("drop all tables")
    # create all tables according to the metadata defined in orm_relations.
    Base.metadata.create_all(engine)

    # interact with the database using session
    Session = sessionmaker(bind=engine)
    session = Session()
    test_handle_request2(session)
    # test_match_query_cancel(session)
