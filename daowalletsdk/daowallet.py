import hashlib
import hmac
import requests
import json
import sys
import logging
import inspect
from numbers import Number

logger = logging.getLogger('daowalletsdk')
logger.addHandler(logging.NullHandler())

__all__ = [u'Wallet', u'API_URL', u'SDK_VERSION', u'WalletException', u'WalletArgumentException',
           'WalletResponseException']

API_URL = u'https://b2b.daowallet.com/api/v2'
SDK_VERSION = u'1.0.0'
AVAILABLE_CURRENCY = (u'BTC', u'ETH')
AVAILABLE_FIAT_CURRENCY = (u'USD', u'EUR')


class WalletException(Exception):
    """Base wallet error."""


class WalletArgumentException(WalletException):
    """Wrong arguments."""


class WalletResponseException(WalletException):
    """Bad response."""


def check_args(fun):
    """Wrapper for arguments checking.
       Check next arguments:
       ...currency must be in the list
       ...fiat_currency must be in the list
       ...amount must be positive float
       ...foreign_id must be string with less than 128 characters
       ...address must be string with less than 128 characters.
    """

    def _check(*arguments):
        info = inspect.getfullargspec(fun) if sys.version_info[0] >= 3 else inspect.getargspec(fun)  # 2.x compatibility
        for index, argument in enumerate(info[0]):
            if index < len(arguments):
                if argument == 'currency':
                    if arguments[index] not in AVAILABLE_CURRENCY:
                        raise WalletArgumentException(
                            u'{} value not allowed, use one of {}.'.format(argument, u', '.join(AVAILABLE_CURRENCY)))
                elif argument == 'fiat_currency':
                    if arguments[index] not in AVAILABLE_FIAT_CURRENCY:
                        raise WalletArgumentException(
                            u'{} value not allowed, use one of {}.'.format(argument,
                                                                          u', '.join(AVAILABLE_FIAT_CURRENCY)))
                elif argument == 'amount':
                    if not isinstance(arguments[index], Number) and not isinstance(arguments[index], bool):
                        raise WalletArgumentException(u'{} must be numeric type.'.format(argument))
                    if arguments[index] <= 0:
                        raise WalletArgumentException(u'{} must be positive.'.format(argument))
                elif argument == 'foreign_id' or argument == 'address':
                    if not isinstance(arguments[index],
                                      str if sys.version_info[0] >= 3 else basestring):  # 2.x compatibility
                        raise WalletArgumentException(u'{} must be string type.'.format(argument))
                    if len(arguments[index]) > 128:
                        raise WalletArgumentException(u'{} too long.'.format(argument))
                    if not arguments[index]:
                        raise WalletArgumentException(u'{} string is empty.'.format(argument))
        return fun(*arguments)

    _check.__doc__ = fun.__doc__
    return _check


class Wallet:
    address_endpoint = u'addresses/take'
    withdrawal_endpoint = u'withdrawal/crypto'
    create_invoice_endpoint = u'invoice/new'
    status_invoice_endpoint = u'invoice/status'
    __logger = logger.getChild('wallet')

    def __init__(self, key, secret, url=API_URL):
        self.key = key
        self.secret = secret.encode(u'utf-8')
        self.url = url.rstrip('/')

    def __get_signature(self, json_msg):
        return hmac.new(self.secret, u''.join(json_msg.split()).encode(u'utf8'), hashlib.sha512).hexdigest()

    def __get_headers(self, signature):
        """Get Headers for request.
           User-Agent for determine sdk requests on backend.
        """
        return {
            u'X-Processing-Key': self.key,
            u'X-Processing-Signature': signature,
            u'Content-type': u'application/json; charset=utf-8',
            u'User-Agent': u'DAOWalletSDK/{} (Language=Python;)'.format(SDK_VERSION)
        }

    def __get_url(self, endpoint):
        """Get full endpoint url. Independent of either
           is url ends with / or
           is endpoint starts with /.
        """
        url = self.url + '/' + endpoint.lstrip('/')
        return url

    def __make_post_request(self, request, url):
        """Make post request with data
           automatically dumps data to json
           and set headers.
        """
        self.__logger.debug('Url requested: {}.'.format(url))
        json_msg = json.dumps(request)
        self.__logger.debug('Request body: {}.'.format(json_msg))
        headers = self.__get_headers(self.__get_signature(json_msg=json_msg))
        self.__logger.debug('Request headers: {}.'.format(headers))
        response = requests.post(url, data=json_msg, headers=headers)
        return self.__process_response(response)

    def __process_response(self, response):
        """Handle most response processing errors."""
        self.__logger.debug('Response body: {}.'.format(response.content))
        result = None
        err = 'Empty response.'
        try:
            result = response.json()
        except json.decoder.JSONDecodeError as e:
            if response.status_code not in (200, 201, 202):
                err = 'Unacceptable status code {}.'.format(response.status_code)
                self.__logger.error(err)
            else:
                err = 'Response is not valid json. {}.'.format(str(e))
                self.__logger.error(err)
        if not result:
            raise WalletResponseException(err)
        else:
            if response.status_code not in (200, 201, 202):
                err = 'Unacceptable status code {}'.format(response.status_code)
                if result.get('error'):
                    err = result['error']
                if result.get('message'):
                    err += ': {}.'.format(result['message'])
                self.__logger.error(err)
                raise WalletResponseException(err)
            else:
                return result

    @check_args
    def get_address(self, foreign_id, currency):
        """Make new account.

           :param foreign_id: new account id.
           :param currency: account crypto currency.
        """
        url = self.__get_url(self.address_endpoint)
        result = self.__make_post_request(dict(foreign_id=foreign_id, currency=currency), url)
        # unwrap response from data field of parent object
        if result.get('data'):
            return result['data']
        else:
            err = 'Response is not valid structure.'
            self.__logger.debug('Response body: {}.'.format(json.dumps(result)))
            self.__logger.error(err)
            raise WalletResponseException(err)

    @check_args
    def make_withdrawal(self, foreign_id, amount, currency, address):
        """Make withdrawal request.

           :param foreign_id: sender account foreign_id.
           :param amount: requested coins amount.
           :param currency: crypto currency for withdrawal.
           :param address: recipient address.
        """
        url = self.__get_url(self.withdrawal_endpoint)
        result = self.__make_post_request(
            dict(foreign_id=foreign_id, amount=amount, currency=currency, address=address),
            url)
        # unwrap response from data field of parent object
        if result.get('data'):
            return result['data']
        else:
            err = 'Response is not valid structure.'
            self.__logger.debug('Response body: {}.'.format(json.dumps(result)))
            self.__logger.error(err)
            raise WalletResponseException(err)

    @check_args
    def make_invoice(self, amount, fiat_currency):
        """Create new invoice.

           :param amount: requested money amount.
           :param fiat_currency: fiat currency which will be used for invoice calculation.
        """
        url = self.__get_url(self.create_invoice_endpoint)
        return self.__make_post_request(dict(amount=amount, fiat_currency=fiat_currency), url)

    @check_args
    def get_invoice(self, foreign_id):
        """Get invoice status information.

           :param foreign_id: invoice foreign_id from 'make_invoice' function  result.
        """
        url = self.__get_url(self.status_invoice_endpoint)
        self.__logger.debug('Get invoice status by id: {}.'.format(foreign_id))
        response = requests.get(url, params=dict(id=foreign_id), headers=self.__get_headers(''))
        return self.__process_response(response)
