"""
Tokenized stocks in the Aave V4 Equities Hub on Base: how much is in the hub, what it is worth,
and how many addresses have supplied stocks, using Envio HyperSync.

Usage:
    export ENVIO_API_TOKEN=...          # free token: https://docs.envio.dev/docs/HyperSync/api-tokens
    python3 equities_hub.py
"""
import json, os, urllib.request

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
HUB = "0xa4d5947eb727a052bae69c593ffc84247ec9864e"  # Aave V4 Equities Hub, Base
STOCKS = {  # token: (name, Chainlink price feed), both from Aave's address book
    "0xb200000000000000000000c2e324d24d7eecd1fb": ("Apple", "0x787f13dEa48Db0897CbCDD985de77809D837F988"),
    "0xb200000000000000000000d9192b6b456483c2e8": ("Amazon", "0x06A8E4b3aBB3B7543d8396FB2B763d22820cB295"),
    "0xb2000000000000000000002d0ba3164cc74f58b7": ("Google", "0x5bF49E0ffA937CE2FfF033c739aD7C634c4D34F2"),
    "0xb2000000000000000000008bc8786b856e61707c": ("Meta", "0x6526aE6797A76123638b863AeE4dD27Ba4E4b27D"),
    "0xb200000000000000000000ab99cfa739e253872b": ("Microsoft", "0xeB10A6c9aa7E537aEd766C08c35Dae35B321b18c"),
    "0xb20000000000000000000078ee7ce2fe4908108c": ("Nvidia", "0x04689a41629776563E6822F76f2e57D148d28513"),
    "0xb2000000000000000000001e800a7f5189430cd0": ("Tesla", "0xFaf869185383a24F8cb00e27BdA6b63B9905DCb4")}
AAVE_CONTRACTS = {"0x9e81c2fde4e34cab3ab1667ca3c932dbaed95f08"}  # Aave's own position manager, not a user
BASE_RPC = "https://mainnet.base.org"
hub = "0x" + "0" * 24 + HUB[2:]

def post(url, body, headers):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "User-Agent": "curl/8", **headers})
    return json.load(urllib.request.urlopen(req, timeout=180))

def price(feed):  # Chainlink latestRoundData, scaled by the feed's decimals
    call = lambda data: post(BASE_RPC, {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": feed, "data": data}, "latest"]}, {})["result"]
    return int(call("0xfeaf968c")[66:130], 16) / 10 ** int(call("0x313ce567"), 16)

# Every transfer of the 7 stock tokens into or out of the hub, since it opened
query = {"from_block": 35_000_000,
         "logs": [{"address": list(STOCKS), "topics": [[TRANSFER], [hub]]},
                  {"address": list(STOCKS), "topics": [[TRANSFER], [], [hub]]}],
         "field_selection": {"log": ["address", "topic1", "topic2", "data"]}}
held = {name: 0 for name, _ in STOCKS.values()}
wallets = {name: set() for name, _ in STOCKS.values()}
while True:
    res = post("https://base.hypersync.xyz/query", query, {"Authorization": f"Bearer {os.environ['ENVIO_API_TOKEN']}"})
    for batch in res["data"]:
        for log in batch.get("logs", []):
            name, sender = STOCKS[log["address"].lower()][0], "0x" + log["topic1"][-40:]
            amount = int(log["data"], 16) / 1e8
            if log["topic2"] == hub:
                held[name] += amount
                if sender not in AAVE_CONTRACTS: wallets[name].add(sender)
            else:
                held[name] -= amount
    if res["next_block"] >= res["archive_height"]: break
    query["from_block"] = res["next_block"]

values = {name: held[name] * price(feed) for name, feed in STOCKS.values()}
print(f"\n{'stock':<10}{'shares':>10}{'value':>14}{'addresses':>11}")
for name in sorted(values, key=values.get, reverse=True):
    print(f"{name:<10}{held[name]:>10,.0f}{'$' + format(values[name], ',.0f'):>14}{len(wallets[name]):>11,}")
print(f"\n${sum(values.values()):,.0f} of tokenized stocks in the hub")
print(f"{len(set().union(*wallets.values())):,} addresses have supplied stocks since 25th Sep")
