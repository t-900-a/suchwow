import requests
import six
import json
import operator
from suchwow import config
from decimal import Decimal


PICOWOW = Decimal('0.00000000001')

class Wallet(object):
    def __init__(self):
        self.host = config.WALLET_HOST
        self.port = config.WALLET_PORT
        self.proto = config.WALLET_PROTO
        self.username = config.WALLET_USER
        self.password = config.WALLET_PASS
        self.endpoint = '{}://{}:{}/json_rpc'.format(
            self.proto, self.host, self.port
        )
        self.auth = requests.auth.HTTPDigestAuth(
            self.username, self.password
        )

        try:
            r = self.height()
            height = r['height']
            self.connected = True
        except:
            self.connected = False

    def make_wallet_rpc(self, method, params={}):
        r = requests.get(
            self.endpoint,
            data=json.dumps({'method': method, 'params': params}),
            auth=self.auth
        )
        if 'error' in r.json():
            return r.json()['error']
        else:
            return r.json()['result']

    def height(self):
        return self.make_wallet_rpc('get_height', {})

    def spend_key(self):
        return self.make_wallet_rpc('query_key', {'key_type': 'spend_key'})['key']

    def view_key(self):
        return self.make_wallet_rpc('query_key', {'key_type': 'view_key'})['key']

    def seed(self):
        return self.make_wallet_rpc('query_key', {'key_type': 'mnemonic'})['key']

    def accounts(self):
        _accounts = self.make_wallet_rpc('get_accounts')
        return [i['account_index'] for i in _accounts['subaddress_accounts']]

    def new_account(self, label=None):
        _account = self.make_wallet_rpc('create_account', {'label': label})
        return _account['account_index']

    def addresses(self, account, addr_indices=None):
        qdata = {'account_index': account}
        if addr_indices:
            qdata['address_index'] = addr_indices
        _addresses = self.make_wallet_rpc('get_address', qdata)
        if 'message' in _addresses:
            return None
        addresses = [None] * (max(map(operator.itemgetter('address_index'), _addresses['addresses'])) + 1)
        for _addr in _addresses['addresses']:
            addresses[_addr['address_index']] = _addr['address']
        return addresses

    def get_address(self, account):
        qdata = {'account_index': account}
        _addresses = self.make_wallet_rpc('get_address', qdata)
        if 'address' in _addresses:
            return _addresses['address']
        else:
            return None

    def new_address(self, account, label=None):
        data = {'account_index': account, 'label': label}
        _address = self.make_wallet_rpc('create_address', data)
        return (_address['address_index'], _address['address'])

    def transfers(self, account, address_indices=[]):
        data = {
            'account_index': account,
            'subaddr_indices': address_indices,
            'in': True,
            'out': True
        }
        _transfers = self.make_wallet_rpc('get_transfers', data)
        return _transfers

    def balances(self, account):
        data = {'account_index': account}
        _balance = self.make_wallet_rpc('get_balance', data)
        return (from_atomic(_balance['balance']), from_atomic(_balance['unlocked_balance']))

    def transfer(self, dest_address, amount, priority, account):
        data = {
            'account_index': account,
            'destinations': [{'address': dest_address, 'amount': to_atomic(amount)}],
            'priority': priority,
            'unlock_time': 0,
            'get_tx_key': True,
            'get_tx_hex': True,
            'new_algorithm': True,
            'do_not_relay': False,
            'ring_size': 22
        }
        transfer = self.make_wallet_rpc('transfer', data)
        return transfer

    def sweep_all(self, account, dest_address):
        data = {
            'address': dest_address,
            'account_index': account,
        }
        sweep = self.make_wallet_rpc('sweep_all', data)
        return sweep

    def incoming_transfers(self, account, transfer_type='all', verbose=True):
        data = {
            'transfer_type': transfer_type,
            'account_index': account,
            'verbose': verbose
        }
        transfers = self.make_wallet_rpc('incoming_transfers', data)
        return transfers



def to_atomic(amount):
    if not isinstance(amount, (Decimal, float) + six.integer_types):
        raise ValueError("Amount '{}' doesn't have numeric type. Only Decimal, int, long and "
                "float (not recommended) are accepted as amounts.")
    return int(amount * 10**11)

def from_atomic(amount):
    return (Decimal(amount) * PICOWOW).quantize(PICOWOW)

def as_wownero(amount):
    return float(Decimal(amount).quantize(PICOWOW))
