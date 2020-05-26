import unittest
from daowalletsdk.daowallet import Wallet, API_URL, SDK_VERSION, check_args, \
    WalletArgumentException, WalletResponseException, AVAILABLE_CURRENCY, AVAILABLE_FIAT_CURRENCY
import random
import string
import json


def get_random_string(uppercase=True, alphanum=True, length=32):
    """ Generate random strings.

        :param uppercase: include uppercase characters
        :param alphanum: include numbers
        :param length: result length
    """
    if uppercase:
        symbols = string.ascii_letters
    else:
        symbols = string.ascii_lowercase
    if alphanum:
        symbols += string.digits
    return u''.join([random.choice(symbols) for _ in range(length)])


class ResponseMock:

    def __init__(self, status, body):
        self.content = body
        self.status_code = status

    def json(self):
        return json.loads(self.content)


class TestWallet(unittest.TestCase):
    def assertRaisesMessageContains(self, expected_exception, expected_message, func, *args, **kwargs):
        """Check exception message contains substring in case of
            python 2.7 not has assertRaisesRegex method in unittest
        """
        exception = None
        try:
            func(*args, **kwargs)
        except Exception as e:
            exception = e
        self.assertIsInstance(exception, expected_exception)
        self.assertIn(expected_message, str(exception))

    def test_init(self):
        key = get_random_string()
        secret = get_random_string()
        url = get_random_string(uppercase=False, alphanum=False, length=16)
        wallet = Wallet(key, secret, url=url)
        self.assertEqual(wallet.key, key)
        self.assertEqual(wallet.secret.decode(u'utf-8'), secret)
        self.assertEqual(wallet.url, url)

    def test_init_default_url(self):
        key = get_random_string()
        secret = get_random_string()
        wallet = Wallet(key, secret)
        self.assertEqual(wallet.key, key)
        self.assertEqual(wallet.secret.decode(u'utf-8'), secret)
        self.assertEqual(wallet.url, API_URL)

    def test_signature(self):
        wallet = Wallet(get_random_string(), u'd1n8rbu0C62ihnvAcjFWVVGItlO6R6Y4')
        msg = dict(foo=u'bar')
        sig = wallet._Wallet__get_signature(json.dumps(msg))
        self.assertEqual(sig,
                         u'3e04d1631e44ede5b75368540755230a38b70f69ed7745f959fc57e9cc33fcdfcad35760c874a8f8ab3f23c4fddee3e1a73cdfe25cac644ef7e9be5a496ecca7')

    def test_get_headers(self):
        key = get_random_string()
        secret = get_random_string()
        signature = get_random_string(alphanum=False, length=64)
        wallet = Wallet(key, secret)
        headers = wallet._Wallet__get_headers(signature)
        self.assertEqual(headers.get(u'X-Processing-Key'), key)
        self.assertEqual(headers.get(u'X-Processing-Signature'), signature)
        self.assertEqual(headers.get(u'Content-type'), u'application/json; charset=utf-8')
        self.assertEqual(headers.get(u'User-Agent'), u'DAOWalletSDK/{} (Language=Python;)'.format(SDK_VERSION))

    def test_get_url(self):
        key = get_random_string()
        secret = get_random_string()
        url = get_random_string(uppercase=False, alphanum=False, length=16)
        endpoint = get_random_string(alphanum=False, length=8)
        wallet = Wallet(key, secret, url=url)
        expected_url = url + '/' + endpoint
        full_url = wallet._Wallet__get_url(endpoint)
        self.assertEqual(full_url, expected_url)
        full_url = wallet._Wallet__get_url('/' + endpoint)
        self.assertEqual(full_url, expected_url)
        wallet = Wallet(key, secret, url=url + '/')
        full_url = wallet._Wallet__get_url(endpoint)
        self.assertEqual(full_url, expected_url)
        full_url = wallet._Wallet__get_url('/' + endpoint)
        self.assertEqual(full_url, expected_url)

    def test_check_args_foreign_id(self):
        @check_args
        def sample_function(foreign_id):
            return foreign_id

        long_str = get_random_string(length=130)
        self.assertRaisesMessageContains(WalletArgumentException, 'foreign_id too long', sample_function, long_str)
        self.assertRaisesMessageContains(WalletArgumentException, 'foreign_id must be string type', sample_function,
                                         None)
        self.assertRaisesMessageContains(WalletArgumentException, 'foreign_id must be string type', sample_function,
                                         555)
        self.assertRaisesMessageContains(WalletArgumentException, 'foreign_id string is empty', sample_function, '')
        normal_str = get_random_string(length=127)
        self.assertEqual(sample_function(normal_str), normal_str)

    def test_check_args_address(self):
        @check_args
        def sample_function(address):
            return address

        long_str = get_random_string(length=130)
        self.assertRaisesMessageContains(WalletArgumentException, 'address too long', sample_function, long_str)
        self.assertRaisesMessageContains(WalletArgumentException, 'address must be string type', sample_function, None)
        self.assertRaisesMessageContains(WalletArgumentException, 'address must be string type', sample_function, 555)
        self.assertRaisesMessageContains(WalletArgumentException, 'address string is empty', sample_function, '')
        normal_str = get_random_string(length=127)
        self.assertEqual(sample_function(normal_str), normal_str)

    def test_check_args_currency(self):
        @check_args
        def sample_function(currency):
            return currency

        cur = get_random_string(length=3)
        self.assertRaisesMessageContains(WalletArgumentException, 'currency value not allowed, use one of',
                                         sample_function, cur)
        self.assertRaisesMessageContains(WalletArgumentException, 'currency value not allowed, use one of',
                                         sample_function, None)
        for each in AVAILABLE_CURRENCY:
            self.assertEqual(sample_function(each), each)

    def test_check_args_fiat_currency(self):
        @check_args
        def sample_function(fiat_currency):
            return fiat_currency

        cur = get_random_string(length=3)
        self.assertRaisesMessageContains(WalletArgumentException, 'fiat_currency value not allowed, use one of',
                                         sample_function, cur)
        self.assertRaisesMessageContains(WalletArgumentException, 'fiat_currency value not allowed, use one of',
                                         sample_function, None)
        for each in AVAILABLE_FIAT_CURRENCY:
            self.assertEqual(sample_function(each), each)

    def test_process_response(self):
        key = get_random_string()
        secret = get_random_string()
        wallet = Wallet(key, secret)

        bad_resp = ResponseMock(400, json.dumps({'error': 'bad', 'message': 'request'}))
        self.assertRaisesMessageContains(WalletResponseException, 'bad: request', wallet._Wallet__process_response,
                                         bad_resp)

        bad_resp = ResponseMock(500, get_random_string(length=64))
        self.assertRaisesMessageContains(WalletResponseException, 'Unacceptable status code',
                                         wallet._Wallet__process_response, bad_resp)

        bad_resp = ResponseMock(200, get_random_string(length=64))
        self.assertRaisesMessageContains(WalletResponseException, 'Response is not valid json.',
                                         wallet._Wallet__process_response, bad_resp)

        bad_resp = ResponseMock(200, '{}')
        self.assertRaisesMessageContains(WalletResponseException, 'Empty response.', wallet._Wallet__process_response,
                                         bad_resp)

        good_resp = ResponseMock(200, json.dumps({'data': 'blah'}))
        self.assertEqual(wallet._Wallet__process_response(good_resp), {'data': 'blah'})


if __name__ == '__main__':
    unittest.main()
