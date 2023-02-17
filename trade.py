from datetime import datetime

from utils import Color, parse_serial_number


class Trade:
    def __init__(self, date, counter_party):
        self.date = date
        self.counter_party = counter_party
        self.in_transactions = []
        self.out_transactions = []
        self.payment = 0
        self.out_value = 0

    def set_out_value(self, out_value):
        self.out_value = out_value

    def set_payment(self, payment):
        self.payment = payment

    def sort_transactions(self):
        self.in_transactions.sort(key=lambda tx: parse_serial_number(tx.moment.moment))
        self.out_transactions.sort(key=lambda tx: parse_serial_number(tx.moment.moment))

    def merge(self, other_trade):
        assert other_trade.counter_party == self.counter_party
        self.in_transactions.extend(other_trade.in_transactions)
        self.out_transactions.extend(other_trade.out_transactions)
        self.sort_transactions()

    def assign_average_price_to_out_transactions(self):
        total_value_left = self.out_value
        unassigned_tx_count = 0
        for transaction in self.out_transactions:
            if transaction.price is not None:
                total_value_left = total_value_left - transaction.price
            else:
                unassigned_tx_count = unassigned_tx_count + 1

        if unassigned_tx_count > 0:
            for transaction in self.out_transactions:
                if transaction.price is None:
                    transaction.price = total_value_left / unassigned_tx_count

    def assign_average_price_to_in_transactions(self):
        total_value_left = self.out_value + self.payment
        unassigned_tx_count = 0
        for transaction in self.in_transactions:
            if transaction.price is not None:
                total_value_left = total_value_left - transaction.price
            else:
                unassigned_tx_count = unassigned_tx_count + 1

        if unassigned_tx_count > 0:
            for transaction in self.in_transactions:
                if transaction.price is None:
                    transaction.price = total_value_left / unassigned_tx_count

    def print(self):
        print(
            f"Trade with {Color.BLUE}{self.counter_party}{Color.ENDC} on {Color.GREEN}{self.date}{Color.ENDC}, "
            f"traded in {Color.RED}{len(self.in_transactions)}{Color.ENDC} moments, "
            f"traded out {Color.RED}{len(self.out_transactions)}{Color.ENDC} moments, ")
        transactions = list(self.in_transactions)
        transactions.extend(self.out_transactions)
        transactions.sort(key=lambda tx: tx.date)
        for transaction in transactions:
            if transaction.tx_type == 'Received Gift':
                print(
                    f"{Color.GREEN}IN{Color.ENDC}: {transaction.moment.moment} on {Color.GREEN}{transaction.date}{Color.ENDC}")
            else:
                print(
                    f"{Color.YELLOW}OUT{Color.ENDC} {transaction.moment.moment} on {Color.GREEN}{transaction.date}{Color.ENDC}")

    def __str__(self):
        return "In: {}, Out: {}".format(
            ','.join([tx.moment.moment for tx in self.in_transactions]),
            ','.join([tx.moment.moment for tx in self.out_transactions])
        )


def get_trades_from_moments(moments):
    users_to_trades = {}
    for identifier in moments:
        moment = moments[identifier]

        for transaction in moment.transactions:

            if transaction.tx_type not in ['Received Gift', 'Sent Gift']:
                continue

            if transaction.price is not None:
                continue

            user = transaction.counter_party
            if user not in users_to_trades:
                users_to_trades[user] = {}

            trade_date = transaction.date[:10]
            if trade_date not in users_to_trades[user]:
                users_to_trades[user][trade_date] = Trade(trade_date, user)

            if transaction.tx_type == 'Received Gift':
                users_to_trades[user][trade_date].in_transactions.append(transaction)
            elif transaction.tx_type in 'Sent Gift':
                users_to_trades[user][trade_date].out_transactions.append(transaction)

    for user in users_to_trades:
        trades = users_to_trades[user]
        # sort by dates
        dates = list(trades.keys())
        dates.sort()
        users_to_trades[user] = {sortedKey: trades[sortedKey] for sortedKey in dates}

    # sort by username
    users = list(users_to_trades.keys())
    users.sort()
    return {sortedKey: users_to_trades[sortedKey] for sortedKey in users}


def merge_trades_for_user(trades):
    dates = list(trades.keys())
    i = 0
    while i < len(dates) - 1:
        date = datetime.strptime(dates[i], '%Y-%m-%d').date()
        next_date = datetime.strptime(dates[i + 1], '%Y-%m-%d').date()
        diff = next_date - date

        if diff.days == 1:
            print("==== MERGE TRADES ====")
            trades[dates[i]].print()
            print("<====>")
            trades[dates[i + 1]].print()
            print("------")

            processed = False
            while not processed:
                response = input(f"Merge these two trades? ({Color.RED}no{Color.ENDC}/yes)\n")
                if response.lower() == 'no' or response == '':
                    processed = True
                    print("==== SKIPPED ====\n")
                elif response.lower() == 'yes':
                    processed = True
                    trades[dates[i]].merge(trades[dates[i + 1]])
                    dates.remove(dates[i + 1])
                    print("==== MERGED ====\n")
                else:
                    print("==== RETRY ====\n")
        i = i + 1

    # sort by dates
    dates.sort()
    return {sortedKey: trades[sortedKey] for sortedKey in dates}


def merge_trades(users_to_trades):
    for user in users_to_trades:
        users_to_trades[user] = merge_trades_for_user(users_to_trades[user])

    # sort by username
    users = list(users_to_trades.keys())
    users.sort()
    return {sortedKey: users_to_trades[sortedKey] for sortedKey in users}


def resolve_trades(users_to_trades):
    resolved = 0
    for user in users_to_trades:
        trades = users_to_trades[user]

        print(f"({Color.RED}{resolved}/{len(users_to_trades)}{Color.ENDC})")
        for date in trades:
            trade = trades[date]
            print("==== ASSIGN TRADE VALUE ====")
            trade.print()
            print("------")
            if len(trade.out_transactions) > 0:
                processed = False
                while not processed:
                    value = input(f"Input the total value of moments sent out ({Color.RED}0{Color.ENDC}): \n")
                    if value == '':
                        value = '0'
                    try:
                        trade.set_out_value(float(value))
                        processed = True
                    except:
                        print("Error parsing number: " + value)
                trade.assign_average_price_to_out_transactions()
                print("==== ASSIGNED PRICE FOR SENT MOMENTS ====")

            if len(trade.in_transactions) > 0:
                processed = False
                while not processed:
                    payment = input("Input the total cash you paid in this trade "
                                    f"(default: {Color.RED}0{Color.ENDC}): \n"
                                    f"{Color.YELLOW}Positive for cash paid, Negative for cash received{Color.ENDC}\n")
                    if payment == '':
                        payment = '0'
                    try:
                        trade.set_payment(float(payment))
                        processed = True
                    except:
                        print("Error parsing number: " + payment)

                print("")
                total_value = trade.out_value + trade.payment
                processed = False
                while not processed:
                    method = input("---- Now you need to assign prices for received moments, choose from 1/2 \n"
                                   f"{Color.YELLOW}1: Assigned ${str(round(total_value, 2))} equally{Color.ENDC}\n"
                                   f"{Color.YELLOW}2: Assigned individually{Color.ENDC}\n")
                    if method == '1':
                        processed = True
                        trade.assign_average_price_to_in_transactions()
                    elif method == '2':
                        print("----")
                        assigned = 0
                        trade.in_transactions.sort(key=lambda tx: parse_serial_number(tx.moment.moment))
                        for transaction in trade.in_transactions:
                            print(f"{Color.RED}{assigned + 1}/{len(trade.in_transactions)}{Color.ENDC} "
                                  f"{transaction.moment.moment}")
                            sub_processed = False
                            while not sub_processed:
                                value = input(
                                    f"Provide value in range [{Color.RED}0{Color.ENDC}, {str(round(total_value, 2))}]:\n")
                                if value == '':
                                    value = '0'
                                try:
                                    value_f = float(value)
                                    if value_f <= total_value:
                                        transaction.price = value_f
                                        total_value = total_value - value_f
                                        assigned = assigned + 1
                                        sub_processed = True
                                    else:
                                        print("Value can't exceed: " + str(total_value))
                                except:
                                    print("Error parsing number: " + value)

                            if assigned < len(trade.in_transactions):
                                response = input(f"For the rest {len(trade.in_transactions) - assigned} moments, "
                                                 f"assigned ${str(round(total_value, 2))} equally? "
                                                 f"({Color.RED}no{Color.ENDC}/yes)\n")
                                if response.lower() == 'yes':
                                    trade.assign_average_price_to_in_transactions()
                                    break
                        processed = True
                    else:
                        print("Invalid input: " + method)
                print("==== ASSIGNED PRICE FOR RECEIVED MOMENTS ====\n")
        resolved = resolved + 1

