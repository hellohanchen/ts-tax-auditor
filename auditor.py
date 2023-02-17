import csv
import os.path
import sys

from moment import Moment, handle_rentals
from pack import get_packs_from_moments, merge_packs, resolve_packs
from trade import get_trades_from_moments, merge_trades, resolve_trades
from transaction import Transaction
from utils import parse_serial_number, parse_counterparty_username, reformat_moment_detail

IN_TX_TYPES = ['Auction Bought', 'Bought', 'Pack', 'Received Gift', 'Reward']
OUT_TX_TYPES = ['Burned', 'Sent Gift', 'Sold', 'Traded In']


def load_from_activities(livetoken_activity_file):
    moments = {}
    with open(livetoken_activity_file, 'r') as in_file:
        reader = csv.DictReader(in_file)
        for line in reader:
            if line['activity'] in IN_TX_TYPES or line['activity'] in OUT_TX_TYPES:
                identifier = line['momentID'] + ' #' + parse_serial_number(line['moment'])
                if identifier not in moments:
                    new_moment = Moment(line['momentID'], reformat_moment_detail(line['moment'].replace(' 路 ', '|')))
                    moments[identifier] = new_moment

                moment = moments[identifier]

                price = None
                if line['activity'] in ['Traded In', 'Burned', 'Reward']:
                    price = 0.0
                elif line['price'] != '':
                    price = float(line['price'])

                transaction = Transaction(moment, line['dateGMT'], line['activity'],
                                          price, parse_counterparty_username(line['counterparty']))
                moment.add_tx(transaction)

    return moments


def load_from_transactions(path='momentTransactions.csv'):
    moments = {}
    with open(path, 'r') as in_file:
        reader = csv.DictReader(in_file)
        for line in reader:
            identifier = line['identifier']
            hash_pos = identifier.find('#')
            if identifier not in moments:
                new_moment = Moment(line['identifier'][:hash_pos - 1], line['moment'])
                moments[identifier] = new_moment

            moment = moments[identifier]

            price = None
            if line['tx_type'] in ['Traded In', 'Burned', 'Reward']:
                price = 0.0
            elif line['price'] != '':
                price = float(line['price'])

            if line['tx_type'] in IN_TX_TYPES or line['tx_type'] in OUT_TX_TYPES:
                transaction = Transaction(moment, line['date'], line['tx_type'], price, line['counter_party'])
                moment.add_tx(transaction)

    return moments


def output_moment(moments, path='result.csv'):
    with open(path, 'w', newline='') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',')
        csv_writer.writerow(['moment_id', 'moment', 'in_type', 'in_counter_party', 'in_price', 'in_date',
                             'out_type', 'out_counter_party', 'out_price', 'out_date', 'profit'])
        for moment_id in moments:
            moment = moments[moment_id]

            i = 0
            while i < len(moment.transactions):
                in_transaction = moment.transactions[i]

                if i == len(moment.transactions) - 1:
                    csv_writer.writerow([moment.moment_id, moment.moment,
                                         in_transaction.tx_type, in_transaction.counter_party,
                                         in_transaction.price, in_transaction.date,
                                         '', '', '', '', ''])
                else:
                    out_transaction = moment.transactions[i + 1]
                    out_price = out_transaction.price * 0.95 if out_transaction.tx_type == 'Sold' else out_transaction.price
                    csv_writer.writerow([moment.moment_id, moment.moment,
                                         in_transaction.tx_type, in_transaction.counter_party,
                                         in_transaction.price, in_transaction.date,
                                         out_transaction.tx_type, out_transaction.counter_party,
                                         out_price, out_transaction.date,
                                         out_price - in_transaction.price])
                i = i + 2


def output_moment_transactions(moments, path='momentTransactions.csv'):
    with open(path, 'w', newline='') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',')
        csv_writer.writerow(['identifier', 'moment', 'tx_type', 'counter_party', 'price', 'date'])

        for identifier in moments:
            moment = moments[identifier]

            i = 0
            while i < len(moment.transactions):
                transaction = moment.transactions[i]
                csv_writer.writerow([identifier, moment.moment,
                                     transaction.tx_type, transaction.counter_party,
                                     '' if transaction.price is None else str(round(transaction.price, 2)),
                                     transaction.date])
                i = i + 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    method = 0
    if len(sys.argv) > 1:
        method = int(sys.argv[1])

    if method < 1:
        moments = load_from_activities(os.path.relpath('activityFeed2.csv'))
        packs = get_packs_from_moments(moments)
        packs = merge_packs(packs)
        resolve_packs(packs)
        output_moment_transactions(moments, path='test/momentWithPacks.csv')

    if method < 2:
        moments = load_from_transactions(path='test/momentWithPacks.csv')
        handle_rentals(moments)
        output_moment_transactions(moments, path='test/momentWithRentals.csv')

    if method < 3:
        moments = load_from_transactions(path='test/momentWithRentals.csv')
        users_to_trades = get_trades_from_moments(moments)
        merge_trades(users_to_trades)
        resolve_trades(users_to_trades)
        output_moment_transactions(moments, path='test/momentWithTrades.csv')

    if method < 4:
        moments = load_from_transactions(path='test/momentWithTrades.csv')
        output_moment(moments, path='test/finalResult.csv')
