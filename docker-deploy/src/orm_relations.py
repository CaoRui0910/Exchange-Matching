from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Double, Numeric, ForeignKey, PrimaryKeyConstraint, Sequence

Base = declarative_base()
trans_id_seq = Sequence("trans_id_seq", start=1)


class Account(Base):
    __tablename__ = "account"
    account_id = Column(Integer, autoincrement=False, primary_key=True)
    balance = Column(Double, nullable=False)

    def __repr__(self):
        return f"Account account_id={self.account_id} balance={self.balance}"


class Position(Base):
    __tablename__ = "position"
    account_id = Column(Integer, ForeignKey("account.account_id"))
    sym = Column(String(15), nullable=False)
    amount = Column(Double, nullable=False)
    PrimaryKeyConstraint(account_id, sym)

    def __repr__(self):
        return f"Position account_id={self.account_id} sym={self.sym} amount={self.amount}"


class Executed(Base):
    __tablename__ = "executed"
    unique_id = Column(Integer, primary_key=True)
    buy_id = Column(Integer, nullable=False)
    buy_account_id = Column(Integer, nullable=False)
    sell_id = Column(Integer, nullable=False)
    sell_account_id = Column(Integer, nullable=False)
    amount = Column(Double, nullable=False)
    price = Column(Double, nullable=False)
    time = Column(Numeric, nullable=False)

    def __repr__(self):
        return f"Executed buy_id = {self.buy_id} sell_id = {self.sell_id} amount = {self.amount} price = {self.price} time = {self.time} buy_account={self.buy_account_id} sell_account={self.sell_account_id}"


class Cancelled(Base):
    __tablename__ = "cancelled"
    trans_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    amount = Column(Double, nullable=False)
    time = Column(Numeric, nullable=False)

    def __repr__(self):
        return f"Cancelled trans_id={self.trans_id} amount={self.amount} time={self.time} account = {self.account_id}"


class SellOrder(Base):
    __tablename__ = "sellorder"
    id = Column(Integer, trans_id_seq, autoincrement=False, primary_key=True)
    account_id = Column(Integer, ForeignKey("account.account_id"))
    sym = Column(String(15), nullable=False)
    amount = Column(Double, nullable=False)
    price_limit = Column(Double, nullable=False)
    placed_time = Column(Numeric, nullable=False)

    def __repr__(self):
        return f"SellOrder id = {self.id} account_id = {self.account_id} sym = {self.sym} amount = {self.amount} price_limit = {self.price_limit} time = {self.placed_time}"


class BuyOrder(Base):
    __tablename__ = "buyorder"
    id = Column(Integer, trans_id_seq, autoincrement=False, primary_key=True)
    account_id = Column(Integer, ForeignKey("account.account_id"))
    sym = Column(String(15), nullable=False)
    amount = Column(Double, nullable=False)
    price_limit = Column(Double, nullable=False)
    placed_time = Column(Numeric, nullable=False)

    def __repr__(self):
        return f"BuyOrder id = {self.id} account_id = {self.account_id} sym = {self.sym} amount = {self.amount} price_limit = {self.price_limit} time = {self.placed_time}"
