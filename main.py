import requests
import csv

from fake_useragent import UserAgent
from tqdm import tqdm

from client import AptosClient


addresses = []
proxies = []
galxe_oat = 0
anniversary_2023 = 0

private_keys_path = './private_keys.csv'
with open(private_keys_path) as f:
    reader = list(csv.reader(f))
    for row in tqdm(reader):
        if row[0] == 'private_key':
            continue
        private_key = row[0]
        proxy = row[1]
        aptos_client = AptosClient(private_key=private_key, proxy=proxy)
        addresses.append(aptos_client.address)
        proxies.append(proxy)

csv_rows = [
    ['address', 'Galxe OAT', 'Aptos ONE Mainnet Anniversary 2023']
]
print('Address\tGalxe OAT\tAptos ONE Mainnet Anniversary 2023')

i = 1
for address, proxy in zip(addresses, proxies):
    csv_row = [address, False, False]

    headers = {
        'authority': 'indexer.mainnet.aptoslabs.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://explorer.aptoslabs.com',
        'referer': 'https://explorer.aptoslabs.com/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': UserAgent().random,
        'x-aptos-client': 'aptos-ts-sdk/1.18.0',
    }

    json_data = {
        'query': '\n    query getOwnedTokens($where_condition: current_token_ownerships_v2_bool_exp!, $offset: Int, $limit: Int, $order_by: [current_token_ownerships_v2_order_by!]) {\n  current_token_ownerships_v2(\n    where: $where_condition\n    offset: $offset\n    limit: $limit\n    order_by: $order_by\n  ) {\n    ...CurrentTokenOwnershipFields\n  }\n}\n    \n    fragment CurrentTokenOwnershipFields on current_token_ownerships_v2 {\n  token_standard\n  token_properties_mutated_v1\n  token_data_id\n  table_type_v1\n  storage_id\n  property_version_v1\n  owner_address\n  last_transaction_version\n  last_transaction_timestamp\n  is_soulbound_v2\n  is_fungible_v2\n  amount\n  current_token_data {\n    collection_id\n    description\n    is_fungible_v2\n    largest_property_version_v1\n    last_transaction_timestamp\n    last_transaction_version\n    maximum\n    supply\n    token_data_id\n    token_name\n    token_properties\n    token_standard\n    token_uri\n    current_collection {\n      collection_id\n      collection_name\n      creator_address\n      current_supply\n      description\n      last_transaction_timestamp\n      last_transaction_version\n      max_supply\n      mutable_description\n      mutable_uri\n      table_handle_v1\n      token_standard\n      total_minted_v2\n      uri\n    }\n  }\n}\n    ',
        'variables': {
            'where_condition': {
                'owner_address': {
                    '_eq': address,
                },
                'amount': {
                    '_gt': 0,
                },
            },
            'offset': 0,
            'limit': 20,
            'order_by': [
                {
                    'last_transaction_version': 'desc',
                },
                {
                    'token_data_id': 'desc',
                },
            ],
        },
    }

    response = requests.post(
        'https://indexer.mainnet.aptoslabs.com/v1/graphql/',
        headers=headers,
        json=json_data,
        proxies={"https": f"http://{proxy}"}
    )
    for row in response.json()['data']['current_token_ownerships_v2']:
        collection_name = row['current_token_data']['current_collection']['collection_name']
        if collection_name == 'Galxe OAT':
            csv_row[1] = True
            galxe_oat += 1
        elif collection_name == 'Aptos ONE Mainnet Anniversary 2023':
            csv_row[2] = True
            anniversary_2023 += 1

    csv_rows.append(csv_row)
    print(f'{i}/{len(addresses)}', end='\t')
    for col in csv_row:
        print(col, end='\t')
    print()
    i += 1

print()
print(f'Galxe OAT: {galxe_oat}/{len(addresses)}')
print(f'Aptos ONE Mainnet Anniversary 2023: {anniversary_2023}/{len(addresses)}')

with open('./nfts.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(csv_rows)
