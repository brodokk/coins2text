# Coins2txt

A simple app to make parsing easier on NeosVR of cryptocurrencies values.

A NeosVR client is available here: `not published yet` and a server is
currently running at: https://coins2txt.neos.spacealicorn.network.

The ticket system handle both server and NeosVR client issues.

## Requirements

Python 3

## Installation

`pip install -r requirements.txt`

## Usage

For run the app just use `python app.py`

```
parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
```

The api used is https://www.coingecko.com except for the NCR value for the
moment who is parsed directly from the NeosVR website.

There is only one endpoint `/price` available for the moment with a `coins`
parameter. Usage example with curl:

```
> curl https://coins2txt.neos.spacealicorn.network/price?coins=bitcoin,polkadot,cardano,ncr,ethereum,dogecoin
63632,43.75,2.16,0.2382318316,4164.4,0.266408
```
