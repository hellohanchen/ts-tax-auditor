import csv
import os.path
import sys
from datetime import datetime
from typing import Dict

from moment import Moment, handle_rentals, sort_moments_by_date
from pack import get_packs_from_moments, merge_packs, resolve_packs
from trade import get_trades_from_moments, merge_trades, resolve_trades
from transaction import Transaction
from utils import parse_serial_number, parse_counterparty_username, reformat_moment_detail

IN_TX_TYPES = ['Auction Bought', 'Bought', 'Pack', 'Received Back', 'Received Gift', 'Rented In', 'Reward']
OUT_TX_TYPES = ['Auction Sold', 'Burned', 'Rented Out', 'Sent Back', 'Sent Gift', 'Sold', 'Traded In']


def load_from_activities(livetoken_activity_file, loaded: Dict | None = None):
    if loaded is None:
        loaded = {}
    with open(livetoken_activity_file, 'r') as in_file:
        reader = csv.DictReader(in_file)
        for record in reader:
            tx_type = record['activity']
            if tx_type in IN_TX_TYPES or tx_type in OUT_TX_TYPES:
                moment_id = record['momentID']
                moment_info = record['moment']

                identifier = moment_id + ' #' + parse_serial_number(moment_info)
                if identifier not in loaded:
                    new_moment = Moment(moment_id, reformat_moment_detail(moment_info.replace(' 路 ', '|')))
                    loaded[identifier] = new_moment

                moment = loaded[identifier]
                date = record['dateGMT']
                if len(moment.transactions) > 0 and date <= moment.transactions[-1].date:
                    continue  # skip old transactions

                price = None
                if record['activity'] in ['Traded In', 'Burned', 'Reward']:
                    price = 0.0
                elif record['price'] != '':
                    price = float(record['price'])

                transaction = Transaction(moment, date, tx_type, price,
                                          parse_counterparty_username(record['counterparty']))
                moment.add_tx(transaction)

    to_exclude = []
    for mid in loaded:
        # remove the last OUT transaction from last audit
        moment = loaded[mid]
        if moment.transactions[0].tx_type in OUT_TX_TYPES and moment.transactions[0].price is not None:
            moment.transactions = moment.transactions[1:]
        if len(moment.transactions) == 0:
            to_exclude.append(mid)

    for mid in to_exclude:
        del loaded[mid]

    return loaded


def load_from_transactions(path='momentTransactions.csv', last_only=False):
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

    if last_only:
        # only keep the last transaction assuming the rest are all audited
        for mid in moments:
            moments[mid].transactions = moments[mid].transactions[-1:]

    return moments


def output_moment(moments, path='result.csv'):
    with open(path, 'w', newline='') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',')
        csv_writer.writerow(['moment_id', 'moment', 'in_type', 'in_counter_party', 'in_price', 'in_date',
                             'out_type', 'out_counter_party', 'out_price', 'out_date', 'profit', 'days_holding'])
        for moment_id in moments:
            moment = moments[moment_id]

            if moment.transactions[0].tx_type in OUT_TX_TYPES:
                i = 1
            else:
                i = 0
            while i < len(moment.transactions):
                in_transaction = moment.transactions[i]

                in_price = in_transaction.price
                if in_transaction.tx_type == 'Received Back' and i >= 2:
                    j = i - 2
                    while moment.transactions[j] == 'Received Back' and j > 2:
                        j = j - 2
                    in_price = moment.transactions[j].price

                if i == len(moment.transactions) - 1:
                    csv_writer.writerow([moment.moment_id, moment.moment,
                                         in_transaction.tx_type, in_transaction.counter_party,
                                         in_price, in_transaction.date,
                                         '', '', '', '', '', ''])
                else:
                    out_transaction = moment.transactions[i + 1]

                    date_diff = datetime.strptime(out_transaction.date[:10], '%Y-%m-%d').date() - \
                           datetime.strptime(in_transaction.date[:10], '%Y-%m-%d').date()

                    out_price = out_transaction.price
                    if out_transaction.tx_type == 'Rented Out':
                        out_price = out_transaction.price + in_price
                    elif out_transaction.tx_type == 'Sold':
                        out_price = out_transaction.price * 0.95

                    csv_writer.writerow([moment.moment_id, moment.moment,
                                         in_transaction.tx_type, in_transaction.counter_party,
                                         in_price, in_transaction.date,
                                         out_transaction.tx_type, out_transaction.counter_party,
                                         out_price, out_transaction.date,
                                         str(round(out_price - in_price, 2)), date_diff.days])
                i = i + 2


def output_moment_transactions(moments, path='momentTransactions.csv'):
    with open(path, 'w', newline='') as out_file:
        csv_writer = csv.writer(out_file, delimiter=',')
        csv_writer.writerow(['identifier', 'moment', 'tx_type', 'counter_party', 'price', 'date'])

        for identifier in moments:
            moment = moment[identifier]

            for transaction in moment.transactions:
                csv_writer.writerow([identifier, moment.moment,
                                     transaction.tx_type, transaction.counter_party,
                                     '' if transaction.price is None else str(round(transaction.price, 2)),
                                     transaction.date])


def output_trade_intermedia_result(moments, resolved):
    output_moment_transactions(moments, path='test/momentWith' + str(resolved) + "Trades.csv")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    method = 0
    last_report = None
    if len(sys.argv) > 1:
        method = int(sys.argv[1])
    if len(sys.argv) > 2:
        last_report = sys.argv[2]

    if method <= 0:
        moments = None
        if last_report is not None:
            moments = load_from_transactions(last_report, True)

        moments = load_from_activities(os.path.relpath('test/2024/activityFeed2024.csv'), moments)  # change me
        output_moment_transactions(moments, path='test/2024/momentsWithTransactions.csv')

    if method <= 1:
        moments = load_from_transactions(path='test/2024/momentsWithTransactions.csv')
        packs = get_packs_from_moments(moments)
        packs = merge_packs(packs)
        resolve_packs(packs)
        output_moment_transactions(moments, path='test/2024/momentWithPacks.csv')

    if method <= 2:
        moments = load_from_transactions(path='test/2024/momentWithPacks.csv')
        handle_rentals(moments)
        output_moment_transactions(moments, path='test/2024/momentWithRentals.csv')

    if method <= 3:
        moments = load_from_transactions(
            path='test/2024/momentWithRentals.csv')  # change this if want to resume from trades handling
        users_to_trades = get_trades_from_moments(moments)
        merge_trades(users_to_trades)
        resolve_trades(users_to_trades, moments, output_trade_intermedia_result)
        output_moment_transactions(moments, path='test/2024/momentWithTrades.csv')

    if method <= 4:
        moments = load_from_transactions(path='test/2024/momentWithTrades.csv')
        moments = sort_moments_by_date(moments)
        output_moment(moments, path='test/2024/finalResult.csv')
