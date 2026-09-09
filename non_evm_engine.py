import asyncio
import httpx
import pandas as pd
from network_config import NATIVE_COINS

async def fetch_bitcoin_balance(address: str) -> float:
    """Queries Mempool.space REST API for total BTC balance (sats to BTC)."""
    url = f"https://mempool.space/api/address/{address}"
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            res = await client.get(url)
            if res.status_code == 200:
                data = res.json()
                funded = data.get("chain_stats", {}).get("funded_txo_sum", 0)
                spent = data.get("chain_stats", {}).get("spent_txo_sum", 0)
                sats_balance = funded - spent
                return sats_balance / 10**8
        except Exception:
            pass
    return 0.0

async def fetch_solana_balance(rpc_url: str, address: str) -> float:
    """Queries Solana JSON-RPC 'getBalance' endpoint (lamports to SOL)."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [address]
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            res = await client.post(rpc_url, json=payload)
            if res.status_code == 200:
                lamports = res.json().get("result", {}).get("value", 0)
                return lamports / 10**9
        except Exception:
            pass
    return 0.0

async def fetch_sui_balance(rpc_url: str, address: str) -> float:
    """Queries Sui JSON-RPC 'suix_getBalance' endpoint (MIST to SUI)."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "suix_getBalance",
        "params": [address]
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            res = await client.post(rpc_url, json=payload)
            if res.status_code == 200:
                mist = int(res.json().get("result", {}).get("totalBalance", 0))
                return mist / 10**9
        except Exception:
            pass
    return 0.0

async def fetch_hyperliquid_user_state(address: str) -> tuple[float, float]:
    """
    Queries Hyperliquid API for both HYPE spot token balance and Perps clearinghouse equity.
    """
    url = "https://api.hyperliquid.xyz/info"
    async with httpx.AsyncClient(timeout=5.0) as client:
        hype_spot_balance = 0.0
        account_value = 0.0
        
        try:
            # 1. Query Spot Balances (HYPE Token)
            spot_payload = {"type": "spotClearinghouseState", "user": address}
            res_spot = await client.post(url, json=spot_payload)
            if res_spot.status_code == 200:
                balances = res_spot.json().get("balances", [])
                for b in balances:
                    if b.get("coin") == "HYPE":
                        hype_spot_balance = float(b.get("total", 0.0))

            # 2. Query Clearinghouse Perps Equity
            perp_payload = {"type": "clearinghouseState", "user": address}
            res_perp = await client.post(url, json=perp_payload)
            if res_perp.status_code == 200:
                margin = res_perp.json().get("marginSummary", {})
                account_value = float(margin.get("accountValue", 0.0))

        except Exception:
            pass
        
    return hype_spot_balance, account_value

async def fetch_non_evm_portfolio(network_name: str, target_rpc: str, wallet_address: str, live_price: float) -> pd.DataFrame:
    native_symbol = NATIVE_COINS[network_name]["symbol"]
    
    if network_name == "Hyperliquid Mainnet":
        hype_balance, account_val = await fetch_hyperliquid_user_state(wallet_address)
        
        records = []
        # Native HYPE token with LIVE market price
        records.append({
            "Asset": "Native (HYPE)",
            "Balance": hype_balance,
            "Price ($)": live_price,
            "Value ($)": hype_balance * live_price
        })
        
        # Perps Margin Equity (denominated in USD)
        if account_val > 0:
            records.append({
                "Asset": "Perps Account Equity (USDC)",
                "Balance": account_val,
                "Price ($)": 1.0,
                "Value ($)": account_val
            })
            
        return pd.DataFrame(records)

    # Standard chains (BTC, SOL, SUI)
    balance = 0.0
    if network_name == "Bitcoin Mainnet":
        balance = await fetch_bitcoin_balance(wallet_address)
    elif network_name == "Solana Mainnet":
        balance = await fetch_solana_balance(target_rpc, wallet_address)
    elif network_name == "Sui Mainnet":
        balance = await fetch_sui_balance(target_rpc, wallet_address)

    return pd.DataFrame([{
        "Asset": f"Native ({native_symbol})",
        "Balance": balance,
        "Price ($)": live_price,
        "Value ($)": balance * live_price
    }])