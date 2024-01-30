from datetime import datetime

from utils import Color


class Pack:
    def __init__(self, date):
        self.date = date
        self.in_transactions = []
        self.payment = 0

    def set_payment(self, payment):
        self.payment = payment

    def merge(self, other_pack):
        self.payment = self.payment + other_pack.payment
        self.in_transactions.extend(other_pack.in_transactions)

    def assign_price_to_transactions(self):
        for transaction in self.in_transactions:
            transaction.price = self.payment / float(len(self.in_transactions))

    def __str__(self):
        return "Pull from pack: {}".format(
            ','.join([tx.moment.moment for tx in self.in_transactions]),
        )


def get_packs_from_moments(moments):
    packs = {}
    for moment_id in moments:
        moment = moments[moment_id]

        for transaction in moment.transactions:

            if transaction.tx_type != 'Pack':
                continue

            if transaction.price is not None:
                continue

            trade_date = transaction.date[:16]
            if trade_date not in packs:
                packs[trade_date] = Pack(trade_date)

            pack = packs[trade_date]
            pack.in_transactions.append(transaction)

    # sort by dates
    dates = list(packs.keys())
    dates.sort()
    return {sortedKey: packs[sortedKey] for sortedKey in dates}


def merge_packs(packs):
    dates = list(packs.keys())
    i = 0
    while i < len(dates) - 1:
        date = datetime.strptime(dates[i][:10], '%Y-%m-%d').date()
        next_date = datetime.strptime(dates[i + 1][:10], '%Y-%m-%d').date()
        diff = next_date - date

        if diff.days <= 1:
            print("==== MERGE PACKS ====")
            print(f"Pack 1 on {Color.GREEN}{dates[i]}{Color.ENDC}, "
                  f"pulled {Color.RED}{len(packs[dates[i]].in_transactions)}{Color.ENDC} moments:")
            for transaction in packs[dates[i]].in_transactions:
                print(f"{transaction.moment.moment} on {Color.GREEN}{transaction.date}{Color.ENDC}")

            print("<====>")
            print(f"Pack 2 on {Color.GREEN}{dates[i + 1]}{Color.ENDC}, "
                  f"pulled {Color.RED}{len(packs[dates[i + 1]].in_transactions)}{Color.ENDC} moments:")
            for transaction in packs[dates[i + 1]].in_transactions:
                print(f"{transaction.moment.moment} on {Color.GREEN}{transaction.date}{Color.ENDC}")

            print("------")

            processed = False
            while not processed:
                response = input(f"Merge these two packs? ({Color.RED}yes{Color.ENDC}/no)\n")
                if response.lower() == 'no':
                    processed = True
                    print("==== SKIPPED ====\n")
                elif response.lower() == 'yes' or response == '':
                    processed = True
                    packs[dates[i + 1]].merge(packs[dates[i]])
                    dates.remove(dates[i])
                    i -= 1
                    print("==== MERGED ====\n")
                else:
                    print("==== RETRY ====\n")
        i = i + 1

    # sort by dates
    dates.sort()
    return {sortedKey: packs[sortedKey] for sortedKey in dates}


def resolve_packs(packs):
    for date in packs:
        pack = packs[date]

        print("==== RESOLVE PACK ====")
        print(f"Pack on {Color.GREEN}{date}{Color.ENDC}, "
              f"pulled {Color.RED}{len(pack.in_transactions)}{Color.ENDC} moments:")
        for transaction in pack.in_transactions:
            print(f"{transaction.moment.moment} on {Color.GREEN}{transaction.date}{Color.ENDC}")
        print("------")

        processed = False
        while not processed:
            payment = input(f"Input the total payment of these packs: "
                            f"(default: {Color.RED}0{Color.ENDC}) \n"
                            f"{Color.YELLOW}For reward/locker room packs, just put 0{Color.ENDC}\n")
            if payment == '':
                payment = '0'
            try:
                pack.set_payment(int(payment))
                processed = True
            except:
                print("Error parsing number.")
        print("==== PACK RESOLVED ====\n")

        pack.assign_price_to_transactions()
