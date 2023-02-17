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
        while i < len(moment.transactions) - 1:
            transaction = moment.transactions[i]
            next_transaction = moment.transactions[i + 1]
            i = i + 1

            if transaction.counter_party == next_transaction.counter_party and \
                    transaction.tx_type == 'Received Gift' and next_transaction.tx_type == 'Sent Gift' and \
                    transaction.price is None and next_transaction.price is None:
                print(f"==== CLEAN {Color.RED}IN{Color.ENDC} RENTAL ====")
                print(f"Moment id: {identifier}\nMoment: {Color.BOLD}{moment.moment}{Color.ENDC}")
                print(f"Received from {Color.BLUE}{transaction.counter_party}{Color.ENDC}"
                      f" on {Color.GREEN}{transaction.date}{Color.ENDC}")
                print(f"Sent back on {Color.GREEN}{next_transaction.date}{Color.ENDC}")

                processed = False
                while not processed:
                    response = input(f"Remove these 2 transactions? ({Color.RED}yes{Color.ENDC}/no)\n")
                    if response.lower() == 'no':
                        response = input(f"Just leave these 2 transactions? ({Color.RED}yes{Color.ENDC}/no)\n")
                        if response.lower() == 'no':
                            payment = input("Did you pay cash in this rental, if so, "
                                            f"how much? ({Color.RED}0{Color.ENDC})\n")
                            if payment == '':
                                payment = '0'
                            try:
                                transaction.price = float(payment)
                                next_transaction.price = 0.0
                                processed = True
                                print("==== UPDATED ====\n")
                            except:
                                print("Error parsing number.")
                        elif response.lower() == 'yes' or response == '':
                            print("==== SKIPPED ====\n")
                            processed = True
                        else:
                            print("==== RETRY ====\n")

                    elif response.lower() == 'yes' or response == '':
                        processed = True
                        if i == 1 and len(moment.transactions) == 2:
                            transaction.price = 0.0
                            next_transaction.price = 0.0
                            print("==== MARKED as 0 ====\n")
                        else:
                            moment.transactions.remove(transaction)
                            moment.transactions.remove(next_transaction)
                            print("==== REMOVED ====\n")
                            i = i - 1

                    else:
                        print("==== RETRY ====\n")

            elif transaction.counter_party == next_transaction.counter_party and \
                    transaction.tx_type == 'Sent Gift' and next_transaction.tx_type == 'Received Gift' and \
                    transaction.price is None and next_transaction.price is None:
                print(f"==== CLEAN {Color.RED}OUT{Color.ENDC} RENTAL ====")
                print("Moment id: {}".format(identifier))
                print(f"Moment: {Color.BOLD}{moment.moment}{Color.ENDC}")
                print(f"Sent to {Color.BLUE}{transaction.counter_party}{Color.ENDC}"
                      f" on {Color.GREEN}{transaction.date}{Color.ENDC}")
                print(f"Received back on {Color.GREEN}{next_transaction.date}{Color.ENDC}")

                processed = False
                while not processed:
                    response = input(f"Remove these 2 transactions? ({Color.RED}yes{Color.ENDC}/no)\n")
                    if response.lower() == 'no':
                        response = input(f"Just leave these 2 transactions? ({Color.RED}yes{Color.ENDC}/no)\n")
                        if response.lower() == 'no':
                            payment = input("Did you earn cash in this rental, if so, "
                                            f"how much? ({Color.RED}0{Color.ENDC})\n")
                            if payment == '':
                                payment = '0'
                            try:
                                transaction.price = float(payment)
                                next_transaction.price = 0.0
                                processed = True
                                print("==== UPDATED ====\n")
                            except:
                                print("Error parsing number.")
                        elif response.lower() == 'yes' or response == '':
                            processed = True
                            print("==== SKIPPED ====\n")
                        else:
                            print("==== RETRY ====\n")

                    elif response.lower() == 'yes' or response == '':
                        processed = True
                        moment.transactions.remove(transaction)
                        moment.transactions.remove(next_transaction)
                        print("==== REMOVED ====\n")
                        i = i - 1

                    else:
                        print("==== RETRY ====\n")
