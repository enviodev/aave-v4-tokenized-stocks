# Tokenized stocks in Aave V4 on Base, with HyperSync

A small Python script that reads Base with [Envio HyperSync](https://docs.envio.dev/docs/HyperSync/overview) to track the tokenized stocks supplied to the Aave V4 Equities Hub.

It pulls every transfer of the 7 stock tokens into and out of the hub since it opened on 25th Sep, adds them up per stock, prices them with Aave's Chainlink feeds and counts the addresses that have supplied stocks. It runs in about 20 seconds.

There's nothing to install beyond Python 3.

## Run it

Get a free API token from the [HyperSync API tokens page](https://docs.envio.dev/docs/HyperSync/api-tokens), then:

```bash
export ENVIO_API_TOKEN=your-token
python3 equities_hub.py
```

## Example output

On 29th Oct 2026:

```
stock         shares         value  addresses
Google        13,052    $3,694,623        267
Nvidia        14,572    $3,102,351        291
Meta           3,377    $2,117,636        119
Tesla          2,610    $1,053,294        124
Apple          2,268      $792,201        164
Amazon         1,941      $474,645        133
Microsoft        621      $327,985        104

$11,562,734 of tokenized stocks in the hub
604 addresses have supplied stocks since 25th Sep
```

The share counts match each token's `balanceOf` for the hub, so the transfers add up to exactly what the hub holds.

## How it works

The script sends one HyperSync query for `Transfer` logs from the 7 stock tokens where the hub is the sender or the receiver, and repeats it from `next_block` until it reaches the chain head. Transfers in are added and transfers out are subtracted. Prices come from each stock's Chainlink feed on Base through a public RPC.

Address counts leave out Aave's own position manager contract, since it isn't a user.

## Use it with a coding agent

Paste this into Claude Code, Cursor or any coding agent from an empty folder:

```
Clone https://github.com/enviodev/aave-v4-tokenized-stocks, read the README, then run equities_hub.py with my ENVIO_API_TOKEN and explain the output. Then change it to print how many addresses supplied stocks each day since the hub opened.
```

## Contracts

All from Aave's address book ([bgd-labs/aave-address-book](https://github.com/bgd-labs/aave-address-book), `AaveV4Base.sol`).

- Aave V4 Equities Hub: `0xa4d5947eb727a052bae69c593ffc84247ec9864e`
- Aave position manager (excluded from address counts): `0x9e81c2fde4e34cab3ab1667ca3c932dbaed95f08`

| Stock | Token | Chainlink feed |
|---|---|---|
| Apple | `0xb200000000000000000000c2e324d24d7eecd1fb` | `0x787f13dEa48Db0897CbCDD985de77809D837F988` |
| Amazon | `0xb200000000000000000000d9192b6b456483c2e8` | `0x06A8E4b3aBB3B7543d8396FB2B763d22820cB295` |
| Google | `0xb2000000000000000000002d0ba3164cc74f58b7` | `0x5bF49E0ffA937CE2FfF033c739aD7C634c4D34F2` |
| Meta | `0xb2000000000000000000008bc8786b856e61707c` | `0x6526aE6797A76123638b863AeE4dD27Ba4E4b27D` |
| Microsoft | `0xb200000000000000000000ab99cfa739e253872b` | `0xeB10A6c9aa7E537aEd766C08c35Dae35B321b18c` |
| Nvidia | `0xb20000000000000000000078ee7ce2fe4908108c` | `0x04689a41629776563E6822F76f2e57D148d28513` |
| Tesla | `0xb2000000000000000000001e800a7f5189430cd0` | `0xFaf869185383a24F8cb00e27BdA6b63B9905DCb4` |
