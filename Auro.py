import xml.etree.ElementTree as ET
import time
import sys
import os
import argparse
from collections import OrderedDict


class OrderBook:
    def __init__(self, book):
        self.book = book
        self.buy = OrderedDict()
        self.sell = OrderedDict()

    def __str__(self):
        return "Buy {0}\nSell {1}".format(self.buy, self.sell)

    def add_order(self, order):
        if order.operation == "BUY":
            self.add_buy_order(order)
        elif order.operation == "SELL":
            self.add_sell_order(order)

    def add_buy_order(self, order):
        if order.price in self.buy:
            self.buy[order.price].append(order)
        else:
            self.buy[order.price] = [order]

    def add_sell_order(self, order):
        if order.price in self.sell:
            self.sell[order.price].append(order)
        else:
            self.sell[order.price] = [order]

    def delete_order(self, order):
        if order.operation == "BUY":
            self.delete_buy_order(order)
        elif order.operation == "SELL":
            self.delete_sell_order(order)

    def delete_buy_order(self, order):
        if order.price in self.buy:
            for i, o in enumerate(self.buy[order.price]):
                if o.orderId == order.orderId:
                    del self.buy[order.price][i]
                    break

    def delete_sell_order(self, order):
        if order.price in self.sell:
            for i, o in enumerate(self.sell[order.price]):
                if o.orderId == order.orderId:
                    del self.sell[order.price][i]
                    break

    def match(self, order):
        if order.operation == "BUY":
            self.match_buy(order)
        elif order.operation == "SELL":
            self.match_sell(order)

    def match_buy(self, order):
        for price, orders in self.sell.items():
            if price <= order.price:
                for o in orders:
                    if o.volume > order.volume:
                        o.volume -= order.volume
                        order.volume = 0
                        break
                    else:
                        order.volume -= o.volume
                        o.volume = 0
                if order.volume == 0:
                    break

    def match_sell(self, order):
        for price, orders in self.buy.items():
            if price >= order.price:
                for o in orders:
                    if o.volume > order.volume:
                        o.volume -= order.volume
                        order.volume = 0
                        break
                    else:
                        order.volume -= o.volume
                        o.volume = 0
                if order.volume == 0:
                    break


class Order:
    def __init__(self, operation, book, price, volume, orderId):
        self.operation = operation
        self.book = book
        self.price = price
        self.volume = volume
        self.orderId = orderId

    def __str__(self):
        return "{0} {1} {2} {3} {4}".format(self.operation, self.book, self.price, self.volume, self.orderId)


def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root


def parse_order(order):
    operation = order.get("operation")
    book = order.get("books")
    if order.get("price") is None:
        price = 0
    else:
        price = float(order.get("price"))
    if order.get("volume") is None:
        volume = 0
    else:
        volume = order.get("volume")
    orderId = order.get("orderId")
    return Order(operation, book, price, volume, orderId)


def process_order(order, order_books):
    if order.book not in order_books:
        order_books[order.book] = OrderBook(order.book)
    if order.operation == "ADD":
        order_books[order.book].add_order(order)
    elif order.operation == "DELETE":
        order_books[order.book].delete_order(order)
    elif order.operation == "MATCH":
        order_books[order.book].match(order)


def main():
    root = parse_xml("orders.xml")

    order_books = {}
    for order in root:
        process_order(parse_order(order), order_books)

    for book, order_book in order_books.items():
        print(book)
        print(order_book)


if __name__ == "__main__":
    main()