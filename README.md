# Exchange-Matching

### 1. Introduction
- Applied Python and SQLAlchemy to implement a robust exchange matching server. In this server, we use xml as an approach to receive and interpret data.
- Each buy order can be matched to a proper sell order. Each sell order can be matched to a proper buy order.
  - When matching buy & sell orders, priority is given to the best matching price.
  - When a pair of buy & sell orders are matched and they have different prices, the price that is used is the price from the older of those two orders.
- Database concurrency

### 2. Usage
- Steps to run server.py:
  - `cd ./docker-deploy/src`
  - `sudo docker-compose up`
- Then, open a new terminal.
- Then, steps to run client.py (our test):
  - `cd ./testing`
  - `python3 client.py`
- Besides, the program `./testing/client2.py` is to test that our server can create correct number of accounts and positions under concurrency situations. A bash file is used to run 10 `./testing/client2.py` concurrently. The program `./testing/client3.py` mixes all requests together under concurrent environment, with the same method to run as `./testing/client2.py`.

### 3. Note
- `./writeup/report.pdf` includes scalability analysis of this project.
