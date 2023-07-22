from orm_relations import *
from sqlalchemy import *
import xml.etree.ElementTree as ET
from utils import *
from sqlalchemy import select
# for root tage "create" and child tag "account": add row to Account table
from server import l


def insert_account(session, account_id, balance, response):
    # Create error: Balance must not be negative
    if (balance < 0):
        ET.SubElement(response, 'error', {'id': str(
            account_id)}).text = "Balance must not be negative"
        return

    # Create error: Ajempting to create an account that already exists is an error.
    global l
    with l:
        if account_exists(session, account_id):
            ET.SubElement(response, 'error', {'id': str(
                account_id)}).text = "Account already exists"
            session.commit()
            return

        account = Account(account_id=account_id, balance=balance)
        session.add(account)
        session.commit()
        ET.SubElement(response, 'created', {'id': str(account_id)})


# This function is used to check whether user want to
# create an account that already exists.
def account_exists(session, account_id):
    account_exists = session.query(Account).filter(
        Account.account_id == account_id).first() is not None
    return account_exists


# for root tage "create" and child tag "symbol": add row to Position table
def insert_postion(session, account_id, sym, amount, response):
    # Disallow short position (amount is negative)
    if (amount < 0):
        ET.SubElement(response, 'error', {'sym': sym, 'id': str(
            account_id)}).text = "Disallow short position"
        return

    # when we use the account, it must exist
    if not account_exists(session, account_id):
        ET.SubElement(response, 'error', {'sym': sym, 'id': str(
            account_id)}).text = "Account does not exist"
        session.commit()
        return
    global l
    with l:
        update_position(session=session, added_amount=amount,
                        account_id=account_id, sym=sym)
        session.commit()
        ET.SubElement(response, 'created', {'sym': sym, 'id': str(account_id)})


# for root tage "transactions" and child tag "query":
# untested
def query(session, account_id, trans_id, response, response_tag='status'):
    buy_order = session.query(BuyOrder).filter(
        BuyOrder.id == trans_id, BuyOrder.account_id == account_id).all()
    sell_order = session.query(SellOrder).filter(
        SellOrder.id == trans_id, SellOrder.account_id == account_id).all()
    executed_order = session.query(Executed).filter(
        or_(and_(Executed.buy_id == trans_id, Executed.buy_account_id == account_id), and_(Executed.sell_id == trans_id, Executed.sell_account_id == account_id))).all()
    cancelled_order = session.query(
        Cancelled).filter(Cancelled.trans_id == trans_id, Cancelled.account_id == account_id).all()
    # if the query result is empty
    if (len(buy_order) + len(sell_order) + len(executed_order) + len(cancelled_order)) == 0:
        ET.SubElement(response, 'error', {
                      'id': str(trans_id)}).text = "This query result is empty"
        return

    open_order = len(buy_order) + len(sell_order)
    # Open and canceled should be mutually exclusive.
    if (open_order != 0) and (len(cancelled_order) != 0):
        # this is not a error case due to clients's input, it is our server's fault.
        print("open and cancelled happen simultaneously")
        return

    response0 = ET.SubElement(response, response_tag, {'id': str(trans_id)})
    if len(buy_order) == 1:
        for an_buy_order in buy_order:
            ET.SubElement(response0, 'open', {
                          'shares': str(an_buy_order.amount)})
    elif len(sell_order) == 1:
        for an_sell_order in sell_order:
            ET.SubElement(response0, 'open', {
                          'shares': str(-an_sell_order.amount)})
    if len(cancelled_order) == 1:
        for an_cancelled_order in cancelled_order:
            ET.SubElement(response0, 'canceled', {'shares': str(
                an_cancelled_order.amount), 'time': str(int(an_cancelled_order.time))})
    if len(executed_order) != 0:
        for an_executed_order in executed_order:
            ET.SubElement(response0, 'executed', {'shares': str(an_executed_order.amount), 'price': str(
                an_executed_order.price), 'time': str(int(an_executed_order.time))})


def update_position(session, added_amount, account_id, sym):
    # check whether sym already exists
    position_exists = session.query(Position).filter_by(
        sym=sym, account_id=account_id).first() is not None
    if position_exists:
        session.execute(update(Position).where(and_(Position.account_id == account_id,
                        Position.sym == sym)).values(amount=Position.amount+added_amount))
    else:
        position = Position(account_id=account_id,
                            sym=sym, amount=added_amount)
        session.add(position)
    # caller's responsibility to commit()


# for root tage "transactions" and child tag "cancel":
# untested
def cancel(session, account_id, trans_id, response):
    # 1. find the open order with trans_id
    global l
    with l:
        buy_order = session.query(BuyOrder).filter(
            BuyOrder.id == trans_id, BuyOrder.account_id == account_id).all()
        sell_order = session.query(SellOrder).filter(
            SellOrder.id == trans_id, SellOrder.account_id == account_id).all()
        # if there is no open order with specified trans_id to cancel
        if (len(buy_order) + len(sell_order)) == 0:
            ET.SubElement(response, 'error', {
                'id': str(trans_id)}).text = "There is no open order with specified trans_id and account_id to cancel"
            session.commit()
            return
        # 2. for each order, add them into cancelled table
        elif len(buy_order) == 1:
            for an_buy_order in buy_order:
                cancelled_order = Cancelled(
                    trans_id=trans_id, account_id=account_id, amount=an_buy_order.amount, time=get_cur_timestamp())
                session.add(cancelled_order)
                # 3. for the buy order: refunds
                added_balance = an_buy_order.price_limit * an_buy_order.amount
                update_balance(session, an_buy_order.account_id, added_balance)
                # 5. delete the open order with trans_id from BuyOrder and SellOrder
                session.delete(an_buy_order)
            session.commit()
        elif len(sell_order) == 1:
            for an_sell_order in sell_order:
                cancelled_order = Cancelled(
                    trans_id=trans_id, account_id=account_id, amount=-an_sell_order.amount, time=get_cur_timestamp())
                session.add(cancelled_order)
                # 4. for the sell order: add position amount
                added_amount = an_sell_order.amount
                update_position(session, added_amount,
                                an_sell_order.account_id, an_sell_order.sym)
            # 5. delete every open order with trans_id from BuyOrder and SellOrder
                session.delete(an_sell_order)
            session.commit()
        else:
            print("unexpected open order status")
            # 6. query Cancelled table and Executed table
            session.commit()
    query(session, account_id, trans_id, response, 'canceled')

# This function is used to check whether there is enough balance to place a buy order:


def lack_balance(session, account_id, needed_balance):
    balance = session.query(Account.balance).filter_by(
        account_id=account_id).scalar()
    return (balance < needed_balance)


# This function is used to check whether there is enough amount of sym to place a sell order:
def lack_amount(session, account_id, needed_amount, sym):
    position = session.query(Position).filter_by(
        account_id=account_id, sym=sym).first()
    if position is None:
        return True
    amount = position.amount
    return (amount < needed_amount)

# for root tage "transactions" and child tag "order": add row to BuyOrder table
# input: trans_id??????????????????


def insert_buy_order(session, account_id, amount, sym, limit_price, response):
    needed_balance = amount * limit_price
    # If insufficient funds are available
    global l
    with l:
        if lack_balance(session, account_id, needed_balance):
            ET.SubElement(response, 'error', {'sym': sym, 'amount': str(
                amount), 'limit': str(limit_price)}).text = "Insufficient funds are available"
            return
        buy_order = BuyOrder(account_id=account_id,
                             sym=sym, amount=amount, price_limit=limit_price, placed_time=get_cur_timestamp())
        session.add(buy_order)
        update_balance(session, account_id, -needed_balance)
        session.commit()
        ET.SubElement(response, 'opened', {'sym': sym, 'amount': str(amount), 'limit': str(
            limit_price), 'id': str(buy_order.id)})
    # for root tage "transactions" and child tag "order": add row to SellOrder table


def insert_sell_order(session, account_id, amount, sym, limit_price, response):
    needed_amount = amount
    # If insufficient amount of symbol are available
    global l
    with l:
        if lack_amount(session, account_id, needed_amount, sym):
            ET.SubElement(response, 'error', {'sym': sym, 'amount': str(-amount), 'limit': str(
                limit_price)}).text = "Insufficient amount of symbol are available"
            return
        sell_order = SellOrder(account_id=account_id,
                               sym=sym, amount=amount, price_limit=limit_price, placed_time=get_cur_timestamp())
        session.add(sell_order)
        update_position(session, -amount, account_id, sym)
        session.commit()
        ET.SubElement(response, 'opened', {'sym': sym, 'amount': str(-amount), 'limit': str(
            limit_price), 'id': str(sell_order.id)})


def update_balance(session, account_id, balance_to_update):
    session.query(Account).filter(Account.account_id == account_id).update(
        {'balance': Account.balance + balance_to_update})
    # caller's responsibility to commit()


# match all open orders for one sym
def match_and_execute(session, sym):
    sell_no_match = False
    buy_no_match = False
    while (True):
        sell_no_match = match_sell_order(session, sym)
        buy_no_match = match_buy_order(session, sym)
        if (sell_no_match and buy_no_match is True):
            break
        else:
            sell_no_match = False
            buy_no_match = False


# for one sell order, match as many buy orders as possible
def match_sell_order(session, sym):
    global l
    with l:
        select_query = select(SellOrder).where(SellOrder.sym == sym).order_by(
            SellOrder.price_limit.asc(), SellOrder.placed_time.asc())
        sell_order_to_match = session.execute(select_query).first()
        if (sell_order_to_match is None):
            return True
        sell_order_to_match = sell_order_to_match[0]
        sell_limit = sell_order_to_match.price_limit
        select_buy_order_query = select(BuyOrder).where(
            and_(BuyOrder.sym == sym, BuyOrder.price_limit >= sell_limit)).order_by(BuyOrder.price_limit.desc(), BuyOrder.placed_time.asc())
        buy_orders = session.scalars(select_buy_order_query).all()
        if len(buy_orders) == 0:
            return True
        for buyorder in buy_orders:
            # print(buyorder)  # for debug
            match_one_pair(session, sell_order_to_match, buyorder, sym)
            if (buyorder.amount == 0):
                session.delete(buyorder)
            if (sell_order_to_match.amount == 0):
                session.delete(sell_order_to_match)
                session.commit()
                return
            session.commit()
        return False


# for one buy order, match as many sell orders as possible
def match_buy_order(session, sym):
    global l
    with l:
        select_query = select(BuyOrder).where(BuyOrder.sym == sym).order_by(
            BuyOrder.price_limit.desc(), BuyOrder.placed_time.asc())
        buy_order_to_match = session.execute(select_query).first()
        if (buy_order_to_match is None):
            return True
        buy_order_to_match = buy_order_to_match[0]
        buy_limit = buy_order_to_match.price_limit
        select_sell_order_query = select(SellOrder).where(
            and_(SellOrder.sym == sym, SellOrder.price_limit <= buy_limit)).order_by(SellOrder.price_limit.asc(), SellOrder.placed_time.asc())
        sell_orders = session.scalars(select_sell_order_query).all()
        if len(sell_orders) == 0:
            return True
        for sellorder in sell_orders:
            # print(sellorder)  # for debug
            match_one_pair(session, sellorder, buy_order_to_match, sym)
            if (sellorder.amount == 0):
                session.delete(sellorder)
            if (buy_order_to_match.amount == 0):
                session.delete(buy_order_to_match)
                session.commit()
                return
            session.commit()  # transaction finish
        return False


def match_one_pair(session, sellorder, buyorder, sym):
    deal_amount = min(sellorder.amount, buyorder.amount)
    deal_price = get_deal_price(sellorder, buyorder)
    total_money = deal_amount*deal_price
    if (deal_price < buyorder.price_limit):  # refund buyer
        update_balance(session, buyorder.account_id,
                       (buyorder.price_limit*deal_amount)-total_money)
    update_position(session, account_id=buyorder.account_id,
                    sym=sym, added_amount=deal_amount)  # add sym to buyer
    update_balance(session, account_id=sellorder.account_id,
                   balance_to_update=total_money)  # add money to seller
    sellorder.amount -= deal_amount
    buyorder.amount -= deal_amount
    insert_executed(session, buy_id=buyorder.id, buy_account_id=buyorder.account_id, sell_id=sellorder.id, sell_account_id=sellorder.account_id,
                    amount=deal_amount, price=deal_price, time=get_cur_timestamp())


def get_deal_price(sell_order, buy_order):
    if (sell_order.placed_time < buy_order.placed_time):
        return sell_order.price_limit
    else:
        return buy_order.price_limit


def insert_executed(session, buy_id, buy_account_id, sell_id, sell_account_id, amount, price, time):
    exe = Executed(buy_id=buy_id, buy_account_id=buy_account_id, sell_id=sell_id, sell_account_id=sell_account_id,
                   amount=amount, price=price, time=time)
    session.add(exe)


# ********for showing the testing results**************#

# One thought:
# a lot of repetition here, only need one function to print all,
# if we have all this tables inherits from one parent class and utilize
# subtype polymorphism and dynamic dispatch


def show_all_accounts(session):
    stmt = select(Account)
    results = session.execute(stmt)
    for entry in results.scalars():
        print(entry)


def show_all_positions(session):
    stmt = select(Position)
    results = session.execute(stmt)
    for entry in results.scalars():
        print(entry)


def show_all_buyOrders(session):
    stmt = select(BuyOrder).order_by(
        BuyOrder.price_limit.desc(), BuyOrder.placed_time.asc())
    results = session.execute(stmt)
    for entry in results.scalars():
        print(entry)


def show_all_sellOrders(session):
    stmt = select(SellOrder).order_by(
        SellOrder.price_limit.asc(), SellOrder.placed_time.asc())
    results = session.execute(stmt)
    for entry in results.scalars():
        print(entry)


def show_all_executed(session):
    stmt = select(Executed)
    results = session.execute(stmt)
    for entry in results.scalars():
        print(entry)


def show_all_cancelled(session):
    stmt = select(Cancelled)
    results = session.execute(stmt)
    for entry in results.scalars():
        print(entry)
