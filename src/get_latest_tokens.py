import requests
import pdb
# import pdb
# # Define the API endpoint URL
# url = "https://www.4byte.directory/api/v1/signatures/"
# # Define the parameters for the request
# # params = {"text_signature": "transfer()"}
# params = {"text_signature__istartswith": "transfer("}
# # params = {"text_signature__iexact": "transfer(address,uint256)"}
# # Make the API request
# response = requests.get(url, params=params)
# pdb.set_trace()
# # Check if the request was successful (status code 200)
# if response.status_code == 200:
#     # Get the response content
#     j = response.json()["results"]

# else:
#     # Print the error message
#     print("Error:", response.text)

# names =  [sig["text_signature"] for sig in j ]
# for i, name in enumerate(names):
#     if name == "airdropTransfer()":
#         print(str(j[i]["hex_signature"]))

# print(sorted(names) )
# print(len(names))
    # "X-CMC_PRO_API_KEY": "718388d3-9be9-4a67-863c-ea7a03776e01",


from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
params = {
    "start": "1",
    "limit": "500",
    "convert": "USD",
    "sort": "market_cap",
    "sort_dir": "desc"
    # "aux": "platform",
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': '718388d3-9be9-4a67-863c-ea7a03776e01',
}


response = requests.get(url, params=params, headers=headers)
if response.status_code == 200:
    data = response.json()['data']
    print(data)
    tokens = []
    for token in data:
        if token['platform'] is not None:
            tokens.append(token)
    names = [token['name'] for token in tokens]
    addresses = [token['platform']['token_address'] for token in tokens]
    print(names)
    print(addresses)
    print(len(addresses))
else:
    print(f"Error {response.status_code}: {response.text}")




# session = Session()
# session.headers.update(headers)

# try:
#   response = session.get(url, params=params)
#   data = json.loads(response.text)["data"]
#   print(len(data))
# except (ConnectionError, Timeout, TooManyRedirects) as e:
#   print(e)
# arr = []
# names = []
# # Print out the data
# for token in data:
#     if token['platform'] is None or token['platform']['name'] == 'Ethereum':
#         continue  # Skip non-ERC-20 tokens and Ethereum itself
#     # print(f"{token['name']} ({token['symbol'].upper()}): {token['platform']['token_address']}")
#     names.append(token['name'])
#     arr.append(token['platform']['token_address'])
# print(names)
# print(arr)