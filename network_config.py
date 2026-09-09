import os

# Base RPC URL endpoints for EVM networks
RPC_NETWORKS = {
    # EVM Networks
    "Ethereum Mainnet": "https://eth-mainnet.g.alchemy.com/v2/",
    "Arbitrum One": "https://arb-mainnet.g.alchemy.com/v2/",
    "Polygon Mainnet": "https://polygon-mainnet.g.alchemy.com/v2/",
    "Optimism Mainnet": "https://opt-mainnet.g.alchemy.com/v2/",
    # Non-EVM Networks
    "Bitcoin Mainnet": "https://mempool.space/api/",
    "Solana Mainnet": "https://api.mainnet-beta.solana.com",
    "Sui Mainnet": "https://fullnode.mainnet.sui.io:443",
    "Hyperliquid Mainnet": "https://api.hyperliquid.xyz/info"
}

# CoinGecko Asset Platform IDs
COINGECKO_PLATFORMS = {
    "Ethereum Mainnet": "ethereum",
    "Arbitrum One": "arbitrum-one",
    "Polygon Mainnet": "polygon-pos",
    "Optimism Mainnet": "optimistic-ethereum",
    "Solana Mainnet": "solana",
    "Sui Mainnet": "sui"
}

# Native Coin Details Mapping
NATIVE_COINS = {
    "Ethereum Mainnet": {"id": "ethereum", "symbol": "ETH", "decimals": 18},
    "Arbitrum One": {"id": "ethereum", "symbol": "ETH", "decimals": 18},
    "Optimism Mainnet": {"id": "ethereum", "symbol": "ETH", "decimals": 18},
    "Polygon Mainnet": {"id": "matic-network", "symbol": "POL", "decimals": 18},
    "Bitcoin Mainnet": {"id": "bitcoin", "symbol": "BTC", "decimals": 8},
    "Solana Mainnet": {"id": "solana", "symbol": "SOL", "decimals": 9},
    "Sui Mainnet": {"id": "sui", "symbol": "SUI", "decimals": 9},
    "Hyperliquid Mainnet": {"id": "hyperliquid", "symbol": "HYPE", "decimals": 8}
}

# Chainlink Aggregator V3 Price Feed Contract Proxies (Asset/USD)
CHAINLINK_FEEDS = {
    "Ethereum Mainnet": {
        "ETH": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        "LINK": "0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c",
        "USDC": "0x8fF732382834621E52354aA07106422839951684"
    },
    "Arbitrum One": {
        "ETH": "0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612",
        "LINK": "0x86E537696423351b600418552154863A0e84055f",
        "USDC": "0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3"
    },
    "Polygon Mainnet": {
        "POL": "0xAB594600376Ec9fD93F8120467719ec170068411",
        "ETH": "0xF9680D99D6C9589E2a93a78A04A279e509205945",
        "USDC": "0xfE4A8cc5b5B2380C17D4907a4aDCEd053721e0B2"
    }
}

# Aave V3 Protocol Data Provider Contract Addresses
AAVE_V3_DATA_PROVIDERS = {
    "Ethereum Mainnet": "0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3",
    "Arbitrum One": "0x69FA0fee221AD11012BAb0FdB45d444D3D5Ce61c",
    "Polygon Mainnet": "0x69FA0fee221AD11012BAb0FdB45d444D3D5Ce61c",
    "Optimism Mainnet": "0x69FA0fee221AD11012BAb0FdB45d444D3D5Ce61c"
}

# Tracked ERC-20 Tokens per Network
TRACKED_TOKENS = {
    "Ethereum Mainnet": {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "UNI":  "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
    },
    "Arbitrum One": {
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "LINK": "0xf97f4df75117a038106268d61d4785199c7ad76f"
    },
    "Polygon Mainnet": {
        "USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        "LINK": "0x53E0bca35eC356BD5ddCfee29C4b2928d96f26a7"
    },
    "Optimism Mainnet": {
        "USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
        "LINK": "0x350a791Bfc2C21F9Ed5d10980Dad2e2638ffa7f6"
    }
}

# ABIs
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"}
]

CHAINLINK_AGGREGATOR_ABI = [
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"name": "roundId", "type": "uint80"},
            {"name": "answer", "type": "int256"},
            {"name": "startedAt", "type": "uint256"},
            {"name": "updatedAt", "type": "uint256"},
            {"name": "answeredInRound", "type": "uint80"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

AAVE_DATA_PROVIDER_ABI = [
    {
        "inputs": [{"name": "asset", "type": "address"}],
        "name": "getReserveData",
        "outputs": [
            {"name": "unbacked", "type": "uint256"},
            {"name": "accruedToTreasuryScaled", "type": "uint256"},
            {"name": "totalAToken", "type": "uint256"},
            {"name": "totalStableDebt", "type": "uint256"},
            {"name": "totalVariableDebt", "type": "uint256"},
            {"name": "liquidityRate", "type": "uint256"},
            {"name": "variableBorrowRate", "type": "uint256"},
            {"name": "stableBorrowRate", "type": "uint256"},
            {"name": "averageStableBorrowRate", "type": "uint256"},
            {"name": "liquidityIndex", "type": "uint256"},
            {"name": "variableBorrowIndex", "type": "uint256"},
            {"name": "lastUpdateTimestamp", "type": "uint40"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "user", "type": "address"}
        ],
        "name": "getUserReserveData",
        "outputs": [
            {"name": "currentATokenBalance", "type": "uint256"},
            {"name": "currentStableDebt", "type": "uint256"},
            {"name": "currentVariableDebt", "type": "uint256"},
            {"name": "principalStableDebt", "type": "uint256"},
            {"name": "scaledVariableDebt", "type": "uint256"},
            {"name": "stableBorrowRate", "type": "uint256"},
            {"name": "liquidityRate", "type": "uint256"},
            {"name": "executionTimestamp", "type": "uint40"},
            {"name": "usageAsCollateralEnabled", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC-20 Transfer Event Signature Topic Hash
TRANSFER_EVENT_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# List of Non-EVM Networks
NON_EVM_NETWORKS = ["Bitcoin Mainnet", "Solana Mainnet", "Sui Mainnet", "Hyperliquid Mainnet"]