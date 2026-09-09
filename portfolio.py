import asyncio
import pandas as pd
import httpx
import streamlit as st
from web3 import AsyncWeb3
from web3.providers import AsyncHTTPProvider
from oracle_fallback import fetch_chainlink_fallback_prices
from network_config import ERC20_ABI, TRACKED_TOKENS, COINGECKO_PLATFORMS, NATIVE_COINS

# 1. Resilient Price Fetcher with TTL Cache (60 sec)
@st.cache_data(ttl=60, show_spinner=False)
def fetch_prices_resilient(target_rpc: str, network_name: str) -> tuple[dict, str]:
    """Synchronous cached wrapper for price retrieval with fallback logic."""
    return asyncio.run(_fetch_prices_resilient_async(target_rpc, network_name))

async def _fetch_prices_resilient_async(target_rpc: str, network_name: str) -> tuple[dict, str]:
    prices = {}
    tokens = TRACKED_TOKENS.get(network_name, {})
    native_info = NATIVE_COINS.get(network_name, {"id": "ethereum", "symbol": "ETH"})
    source_used = "CoinGecko API"

    # Tier 1: CoinGecko API
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=3.0) as client:
            native_url = f"https://api.coingecko.com/api/v3/simple/price?ids={native_info['id']}&vs_currencies=usd"
            res_native = await client.get(native_url, headers=headers)
            if res_native.status_code == 200:
                prices[native_info["symbol"]] = res_native.json().get(native_info["id"], {}).get("usd", 0.0)

            if tokens:
                platform_id = COINGECKO_PLATFORMS.get(network_name, "ethereum")
                addresses = ",".join(tokens.values())
                token_url = f"https://api.coingecko.com/api/v3/simple/token_price/{platform_id}?contract_addresses={addresses}&vs_currencies=usd"
                res_tokens = await client.get(token_url, headers=headers)
                if res_tokens.status_code == 200:
                    tokens_json = res_tokens.json()
                    for symbol, addr in tokens.items():
                        prices[symbol] = tokens_json.get(addr.lower(), {}).get("usd", 0.0)
    except Exception:
        prices = {}

    # Tier 2: Chainlink On-Chain Oracle Fallback
    native_sym = native_info["symbol"]
    if not prices.get(native_sym) or prices.get(native_sym) == 0.0:
        source_used = "Chainlink Decentralized Oracle (On-Chain)"
        chainlink_prices = await fetch_chainlink_fallback_prices(target_rpc, network_name)
        for asset, p_val in chainlink_prices.items():
            if p_val > 0:
                prices[asset] = p_val

    # Tier 3: Defaults
    if prices.get("USDC", 0.0) == 0.0:
        prices["USDC"] = 1.0

    return prices, source_used

# 2. Portfolio Fetcher with TTL Cache (300 sec)
@st.cache_data(ttl=300, show_spinner=False)
def fetch_portfolio_cached(target_rpc: str, wallet_address: str, network_name: str) -> pd.DataFrame:
    """Synchronous cached wrapper for fetching portfolio balances."""
    return asyncio.run(_fetch_portfolio_async(target_rpc, wallet_address, network_name))

async def _fetch_portfolio_async(target_rpc: str, wallet_address: str, network_name: str) -> pd.DataFrame:
    w3 = AsyncWeb3(AsyncHTTPProvider(target_rpc))
    user_checksum = AsyncWeb3.to_checksum_address(wallet_address)
    tokens = TRACKED_TOKENS.get(network_name, {})
    native_info = NATIVE_COINS.get(network_name, {"id": "ethereum", "symbol": "ETH"})
    
    prices, _ = fetch_prices_resilient(target_rpc, network_name)
    raw_native_balance = await w3.eth.get_balance(user_checksum)
    
    native_symbol = native_info["symbol"]
    native_balance = raw_native_balance / 10**18
    native_price = prices.get(native_symbol, 0.0)
    
    results = [{
        "Asset": f"Native ({native_symbol})",
        "Balance": native_balance,
        "Price ($)": native_price,
        "Value ($)": native_balance * native_price
    }]

    async def _fetch_erc20(symbol, addr):
        try:
            contract = w3.eth.contract(address=AsyncWeb3.to_checksum_address(addr), abi=ERC20_ABI)
            decimals, raw_bal = await asyncio.gather(
                contract.functions.decimals().call(),
                contract.functions.balanceOf(user_checksum).call()
            )
            bal = raw_bal / (10 ** decimals)
            if bal > 0:
                p = prices.get(symbol, 0.0)
                return {"Asset": symbol, "Balance": bal, "Price ($)": p, "Value ($)": bal * p}
        except Exception:
            pass
        return None

    erc20_results = await asyncio.gather(*[_fetch_erc20(s, a) for s, a in tokens.items()])
    for item in erc20_results:
        if item:
            results.append(item)

    return pd.DataFrame(results)