class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def parse_serial_number(moment_detail):
    hash_pos = moment_detail.find('#')
    return moment_detail[hash_pos+1:]


def parse_counterparty_username(livetoken_counter_party):
    start = livetoken_counter_party.find('(')
    end = livetoken_counter_party.find(')')

    if start != -1:
        return livetoken_counter_party[start + 1:end]
    else:
        return livetoken_counter_party


def reformat_moment_detail(livetoken_moment_detail):
    delimiter = '|'
    pos1 = livetoken_moment_detail.find(delimiter)
    pos2 = livetoken_moment_detail.find(delimiter, pos1 + 1)
    pos3 = livetoken_moment_detail.find(delimiter, pos2 + 1)
    pos4 = livetoken_moment_detail.find(delimiter, pos3 + 1)
    pos5 = livetoken_moment_detail.find(delimiter, pos4 + 1)
    pos6 = livetoken_moment_detail.find(delimiter, pos5 + 1)

    delimiter = ' | '

    return livetoken_moment_detail[pos5 + 1:pos6] + delimiter + livetoken_moment_detail[pos4 + 1:pos5] + delimiter + \
           livetoken_moment_detail[:pos1] + delimiter + \
           livetoken_moment_detail[pos6 + 1:] + delimiter + livetoken_moment_detail[pos3 + 1:pos4]
