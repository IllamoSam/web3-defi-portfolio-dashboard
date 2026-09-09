import asyncio
import pandas as pd
import streamlit as st
from web3 import AsyncWeb3
from web3.providers import AsyncHTTPProvider
from network_config import AAVE_V3_DATA_PROVIDERS, TRACKED_TOKENS, AAVE_DATA_PROVIDER_ABI

# Cache Aave APYs & positions for 60 seconds
@st.cache_data(ttl=60, show_spinner=False)
def fetch_aave_yields_cached(target_rpc: str, wallet_address: str, network_name: str) -> pd.DataFrame:
    """Synchronous cached wrapper for fetching Aave V3 yield positions."""
    return asyncio.run(_fetch_aave_yields_async(target_rpc, wallet_address, network_name))

async def _fetch_aave_yields_async(target_rpc: str, wallet_address: str, network_name: str) -> pd.DataFrame:
    provider_address = AAVE_V3_DATA_PROVIDERS.get(network_name)
    tokens = TRACKED_TOKENS.get(network_name, {})

    if not provider_address or not tokens:
        return pd.DataFrame()

    w3 = AsyncWeb3(AsyncHTTPProvider(target_rpc))
    user_addr = AsyncWeb3.to_checksum_address(wallet_address)
    provider_contract = w3.eth.contract(
        address=AsyncWeb3.to_checksum_address(provider_address), 
        abi=AAVE_DATA_PROVIDER_ABI
    )

    async def _fetch_reserve(symbol, token_addr):
        try:
            asset_addr = AsyncWeb3.to_checksum_address(token_addr)
            reserve_data, user_reserve = await asyncio.gather(
                provider_contract.functions.getReserveData(asset_addr).call(),
                provider_contract.functions.getUserReserveData(asset_addr, user_addr).call()
            )
            
            supply_apy = (reserve_data[5] / 1e27) * 100
            atoken_balance_raw = user_reserve[0]
            decimals = 6 if symbol == "USDC" else 18
            supplied_balance = atoken_balance_raw / (10 ** decimals)

            if supplied_balance > 0:
                return {
                    "Protocol": "Aave V3",
                    "Network": network_name,
                    "Asset": symbol,
                    "Supplied Amount": supplied_balance,
                    "Supply APY (%)": supply_apy,
                    "Est. Annual Earnings": supplied_balance * (supply_apy / 100)
                }
        except Exception:
            pass
        return None

    results = await asyncio.gather(*[_fetch_reserve(s, a) for s, a in tokens.items()])
    return pd.DataFrame([item for item in results if item is not None])