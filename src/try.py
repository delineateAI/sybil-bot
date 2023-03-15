import requests
import pdb
# Define the API endpoint URL
url = "https://www.4byte.directory/api/v1/signatures/"
# Define the parameters for the request
# params = {"text_signature": "transfer()"}
params = {"text_signature__istartswith": "transfer("}
# params = {"text_signature__iexact": "transfer(address,uint256)"}
# Make the API request
response = requests.get(url, params=params)
pdb.set_trace()
# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Get the response content
    j = response.json()["results"]

else:
    # Print the error message
    print("Error:", response.text)

names =  [sig["text_signature"] for sig in j ]
for i, name in enumerate(names):
    if name == "airdropTransfer()":
        print(str(j[i]["hex_signature"]))

print(sorted(names) )
print(len(names))




    # # extract the function signature
    # signature = tx_data[:10].hex()

    # # define a dictionary of function signatures and their argument types
    # function_sigs = {
    #     'a9059cbb': ('address', 'uint256'),  # transfer(address,uint256)
    #     # add more function signatures and their argument types here as needed
    # }

    # # check if the function signature is known
    # if signature not in function_sigs:
    #     return None, None

    # arg_types = function_sigs[signature]

    # # extract the arguments
    # args = []
    # for i in range(len(arg_types)):
    #     start = 10 + i * 64
    #     end = start + 64
    #     arg_data = tx_data[start:end]
    #     if arg_types[i] == 'address':
    #         args.append(w3.toChecksumAddress('0x' + arg_data[24:]))
    #     elif arg_types[i] == 'uint256':
    #         args.append(int('0x' + arg_data, 16))

    # return signature, args