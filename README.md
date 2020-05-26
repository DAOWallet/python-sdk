# Python SDK for DAOWallet API

This project provides convenient class for using DAOWallet API

## Getting Started

### Installing

You can install this package from pip

```
pip install daowalletsdk
```

## Using

Firstly you need to import main class

```
from daowalletsdk import Wallet
```

Than create object using your key and secret

```
wallet = Wallet(key, secret)
```

Also you can pass custom url

```
wallet = Wallet(key, secret, url=url)
```

You can get information about version and available currencies through next imports

```
from daowalletsdk import SDK_VERSION, AVAILABLE_CURRENCY, AVAILABLE_FIAT_CURRENCY
```

### Methods

Get new account

```
wallet.get_address(foreign_id, currency)
```

Make withdrawal from account with foreign_id to address

```
wallet.make_withdrawal(foreign_id, amount, currency, address)
```

Make invoice

```
wallet.make_invoice(amount, fiat_currency)
```

Get invoice information by id
```
wallet.get_invoice(foreign_id)
```

### Error handling

Base exception class

```
from daowalletsdk import WalletException
```

Separate exceptions for arguments check and for server response check

```
from daowalletsdk import WalletArgumentException, WalletResponseException
```

For capturing network problems use requests library exceptions (for example timeout error)

```
from requests.exceptions import Timeout
```

### Logging

Package uses builtin python logging.
You can enable logging by settings base config

```
import logging
logging.basicConfig(level=logging.DEBUG)
```

The package logger namespace is daowalletsdk.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details
