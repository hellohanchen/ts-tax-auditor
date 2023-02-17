class Transaction:
    def __init__(self, moment, date, tx_type, price, counter_party):
        self.moment = moment
        self.date = date
        self.tx_type = tx_type
        self.price = price
        self.counter_party = counter_party

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.date, self.tx_type, self.price, self.counter_party)
