from utils import Color


class Moment:
    def __init__(self, moment_id, moment):
        self.moment_id = moment_id
        self.moment = moment
        hash_pos = moment.find('#')
        self.serial = moment[hash_pos + 1:]
        self.transactions = []

    def add_tx(self, transaction):
        self.transactions.append(transaction)

    def sort_tx(self):
        self.transactions.sort(key=lambda t: t.counter_party)

    def get_identifier(self):
        return self.moment_id + ' #' + self.serial


def sort_moments_by_id(moments):
    moment_ids = list(moments.keys())
    moment_ids.sort(key=lambda key: int(key[:key.find('#') - 1]))
    return {sortedKey: moments[sortedKey] for sortedKey in moment_ids}


def sort_moments_by_date(moments):
    moment_ids = list(moments.keys())
    moment_ids.sort(key=lambda key: moments[key].transactions[0].date)
    return {sortedKey: moments[sortedKey] for sortedKey in moment_ids}


def handle_rentals(moments):
    for identifier in moments:
        moment = moments[identifier]

        i = 0
        total_tx = len(moment.transactions)
        while i < len(moment.transactions) - 1:
            transaction = moment.transactions[i]
            next_transaction = moment.transactions[i + 1]
            i = i + 1

            if transaction.counter_party == next_transaction.counter_party and \
                    transaction.tx_type == 'Received Gift' and next_transaction.tx_type == 'Sent Gift' and \
                    transaction.price is None and next_transaction.price is None:
                print(f"==== CLEAN {Color.RED}IN{Color.ENDC} RENTAL ====")
                print(f"Moment id: {identifier}, total transactions: {Color.RED}{total_tx}{Color.ENDC}\n"
                      f"Moment: {Color.BOLD}{moment.moment}{Color.ENDC}, ")
                print(f"Received from {Color.BLUE}{transaction.counter_party}{Color.ENDC}"
                      f" on {Color.GREEN}{transaction.date}{Color.ENDC}")
                print(f"Sent back on {Color.GREEN}{next_transaction.date}{Color.ENDC}")

                processed = False
                while not processed:
                    is_rental = input(f"Are these 2 transactions from a rental? ({Color.RED}yes{Color.ENDC}/no)\n")
                    if is_rental.lower() == 'no':
                        should_remove = input(f"Remove these 2 transactions? ({Color.RED}yes{Color.ENDC}/no)\n")
                        if should_remove.lower() == 'yes' or should_remove == '':
                            processed = True
                            transaction.price = 0.0
                            next_transaction.price = 0.0
                            print("==== MARKED as 0 ====\n")
                        elif should_remove.lower() == 'no':
                            processed = True
                            print("==== SKIPPED ====\n")
                        else:
                            print("==== RETRY ====\n")

                    elif is_rental.lower() == 'yes' or is_rental == '':
                        rental_fee = input(
                            f"How much {Color.BOLD}cash{Color.ENDC} did you pay? ({Color.RED}0{Color.ENDC})\n")
                        if rental_fee == '':
                            rental_fee = '0'
                        try:
                            transaction.price = float(rental_fee)
                            transaction.tx_type = 'Rented In'
                            next_transaction.price = 0.0
                            next_transaction.tx_type = 'Returned Back'
                            processed = True
                            print("==== UPDATED ====\n")
                        except:
                            print("Error parsing number.")
                    else:
                        print("==== RETRY ====\n")

            elif transaction.counter_party == next_transaction.counter_party and \
                    transaction.tx_type == 'Sent Gift' and next_transaction.tx_type == 'Received Gift' and \
                    transaction.price is None and next_transaction.price is None:
                print(f"==== CLEAN {Color.RED}OUT{Color.ENDC} RENTAL ====")
                print(f"Moment id: {identifier}, total transactions: {Color.RED}{total_tx}{Color.ENDC}\n"
                      f"Moment: {Color.BOLD}{moment.moment}{Color.ENDC}, ")
                print(f"Sent to {Color.BLUE}{transaction.counter_party}{Color.ENDC}"
                      f" on {Color.GREEN}{transaction.date}{Color.ENDC}")
                print(f"Received back on {Color.GREEN}{next_transaction.date}{Color.ENDC}")

                processed = False
                while not processed:
                    is_rental = input(f"Are these 2 transactions from a rental? ({Color.RED}yes{Color.ENDC}/no)\n")
                    if is_rental.lower() == 'no':
                        should_remove = input(f"Remove these 2 transactions? ({Color.RED}yes{Color.ENDC}/no)\n")
                        if should_remove.lower() == 'yes' or should_remove == '':
                            processed = True
                            moment.transactions.remove(transaction)
                            moment.transactions.remove(next_transaction)
                            print("==== REMOVED ====\n")
                            i = i - 1
                        elif should_remove.lower() == 'no':
                            processed = True
                            print("==== SKIPPED ====\n")
                        else:
                            print("==== RETRY ====\n")

                    elif is_rental.lower() == 'yes' or is_rental == '':
                        rental_fee = input(
                            f"How much {Color.BOLD}cash{Color.ENDC} did you earn? ({Color.RED}0{Color.ENDC})\n")
                        if rental_fee == '':
                            rental_fee = '0'
                        try:
                            transaction.price = float(rental_fee)
                            transaction.tx_type = 'Rented Out'
                            next_transaction.price = 0.0
                            next_transaction.tx_type = 'Received Back'
                            processed = True
                            print("==== UPDATED ====\n")
                        except:
                            print("Error parsing number.")
                    else:
                        print("==== RETRY ====\n")
