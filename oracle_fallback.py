import asyncio
from web3 import AsyncWeb3
from web3.providers import AsyncHTTPProvider
from network_config import CHAINLINK_FEEDS, CHAINLINK_AGGREGATOR_ABI

async def get_chainlink_price(w3: AsyncWeb3, feed_address: str) -> float:
    """Reads latestRoundData from a Chainlink Price Feed contract."""
    try:
        contract = w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(feed_address),
            abi=CHAINLINK_AGGREGATOR_ABI
        )
        decimals, round_data = await asyncio.gather(
            contract.functions.decimals().call(),
            contract.functions.latestRoundData().call()
        )
        raw_price = round_data[1]
        if raw_price > 0:
            return float(raw_price / (10 ** decimals))
    except Exception:
        pass
    return 0.0

async def fetch_chainlink_fallback_prices(target_rpc: str, network_name: str) -> dict:
    """Fetches asset prices directly from on-chain Chainlink smart contracts."""
    w3 = AsyncWeb3(AsyncHTTPProvider(target_rpc))
    feeds = CHAINLINK_FEEDS.get(network_name, {})
    prices = {}

    tasks = [get_chainlink_price(w3, addr) for addr in feeds.values()]
    results = await asyncio.gather(*tasks)

    for symbol, price in zip(feeds.keys(), results):
        if price > 0:
            prices[symbol] = price

    return prices