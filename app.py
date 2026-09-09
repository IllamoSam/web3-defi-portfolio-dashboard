import asyncio
import os
from turtle import pd
import streamlit as st
import plotly.express as px
from web3 import Web3
from pnl_engine import calculate_pnl_analytics
from non_evm_engine import fetch_non_evm_portfolio
from non_evm_analytics import fetch_sui_yields, fetch_hyperliquid_yields, calculate_non_evm_pnl
from portfolio import fetch_portfolio_cached, fetch_prices_resilient
from yield_tracker import fetch_aave_yields_cached
from network_config import RPC_NETWORKS, NATIVE_COINS, NON_EVM_NETWORKS
from styles import apply_custom_css

st.set_page_config(page_title="Multi-Chain Web3 & DeFi Dashboard", layout="wide")
apply_custom_css()
st.title("🌐 Multi-Chain Web3 & DeFi Dashboard")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Network Configuration")

selected_network = st.sidebar.selectbox(
    "Select Blockchain Network:",
    options=list(RPC_NETWORKS.keys()),
    index=0
)

user_api_key = st.sidebar.text_input(
    "Enter Alchemy Key or Custom RPC URL:",
    type="password",
    help="Your key remains private to your session and is not stored."
)

if st.sidebar.button("🧹 Clear Cache & Force Refresh"):
    st.cache_data.clear()
    st.sidebar.success("Cache successfully cleared!")

# Safe RPC string resolution
default_key = os.getenv("DEFAULT_ALCHEMY_KEY", "")
active_key = user_api_key if user_api_key else default_key

if user_api_key.startswith("http://") or user_api_key.startswith("https://"):
    target_rpc = user_api_key
else:
    target_rpc = f"{RPC_NETWORKS[selected_network]}{active_key}"

# --- Main Page Inputs ---
st.subheader("Account Portfolio Lookup")

wallet_input = st.text_input("Enter Wallet Address / Public Key:", placeholder="EVM (0x...), BTC, SOL, SUI")

if st.button("Fetch Portfolio & Yield Data"):
    if not wallet_input:
        st.warning("Please enter a wallet address.")
    else:
        try:
            tab1, tab2, tab3 = st.tabs(["💰 Wallet Balances", "🌾 Aave V3 Yield Positions", "📈 PnL Analytics"])

            # ==========================================
            # DATA INGESTION: NON-EVM PATH
            # ==========================================
            if selected_network in NON_EVM_NETWORKS:
                prices, price_source = fetch_prices_resilient(target_rpc, selected_network)
                native_sym = NATIVE_COINS[selected_network]["symbol"]
                live_price = prices.get(native_sym, 0.0)

                df_portfolio = asyncio.run(
                    fetch_non_evm_portfolio(selected_network, target_rpc, wallet_input, live_price)
                )

                # Tab 1: Balances
                with tab1:
                    st.caption(f"🟢 Price Feed: **{price_source}**")
                    st.dataframe(df_portfolio, use_container_width=True)

                # Tab 2: Yields
                with tab2:
                    if selected_network == "Sui Mainnet":
                        df_yields = asyncio.run(fetch_sui_yields(target_rpc, wallet_input))
                    elif selected_network == "Hyperliquid Mainnet":
                        df_yields = asyncio.run(fetch_hyperliquid_yields(wallet_input))
                    else:
                        df_yields = pd.DataFrame()

                    if not df_yields.empty:
                        st.dataframe(df_yields, use_container_width=True)
                    else:
                        st.info(f"No active yield or staking positions detected on {selected_network}.")

                # Tab 3: PnL Analytics
                with tab3:
                    df_pnl = asyncio.run(calculate_non_evm_pnl(selected_network, df_portfolio))
                    if not df_pnl.empty:
                        st.dataframe(df_pnl, use_container_width=True)
                    else:
                        st.info("No asset data available to compute PnL analytics.")

            else:
                # ==========================================
                # DATA INGESTION: EVM PATH
                # ==========================================
                w3 = Web3(Web3.HTTPProvider(target_rpc))
                
                if not w3.is_connected():
                    st.error(f"Failed to connect to {selected_network}. Verify your RPC Key.")
                else:
                    st.success(f"Connected to {selected_network} | Block: #{w3.eth.block_number:,}")
                    
                    # Retrieve price feed provenance
                    _, price_source = fetch_prices_resilient(target_rpc, selected_network)
                    if "Chainlink" in price_source:
                        st.warning(f"⚠️ Primary REST API throttled. Pricing powered by: **{price_source}**")
                    else:
                        st.caption(f"🟢 Active Price Feed: **{price_source}**")

                    

                    with tab1:
                        with st.spinner("Fetching token balances..."):
                            df_portfolio = fetch_portfolio_cached(target_rpc, wallet_input, selected_network)
                            
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.subheader("Asset Breakdown")
                                st.dataframe(
                                    df_portfolio.style.format({
                                        "Balance": "{:,.4f}",
                                        "Price ($)": "${:,.2f}",
                                        "Value ($)": "${:,.2f}"
                                    }),
                                    use_container_width=True
                                )
                            with col2:
                                st.subheader("Allocation")
                                if df_portfolio["Value ($)"].sum() > 0:
                                    fig = px.pie(df_portfolio, values="Value ($)", names="Asset")
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("No non-zero balances available to chart.")

                    with tab2:
                        with st.spinner("Querying Aave V3 smart contracts..."):
                            df_yields = fetch_aave_yields_cached(target_rpc, wallet_input, selected_network)
                            
                            if not df_yields.empty:
                                st.subheader("Active Supply Positions")
                                st.dataframe(
                                    df_yields.style.format({
                                        "Supplied Amount": "{:,.4f}",
                                        "Supply APY (%)": "{:.2f}%",
                                        "Est. Annual Earnings": "{:,.4f}"
                                    }),
                                    use_container_width=True
                                )
                            else:
                                st.info(f"No active Aave V3 positions found on {selected_network} for this address.")

                    with tab3:
                        with st.spinner("Analyzing on-chain transfer logs (eth_getLogs)..."):
                            df_pnl = asyncio.run(
                                calculate_pnl_analytics(target_rpc, wallet_input, selected_network, df_portfolio)
                        )
                        
                            if not df_pnl.empty:
                                # Summary Metrics
                                tot_cost = df_pnl["Cost Basis ($)"].sum()
                                tot_val = df_pnl["Current Value ($)"].sum()
                                tot_pnl = df_pnl["Unrealized PnL ($)"].sum()
                                tot_roi = ((tot_val - tot_cost) / tot_cost * 100) if tot_cost > 0 else 0.0

                                m1, m2, m3 = st.columns(3)
                                m1.metric("Total Cost Basis", f"${tot_cost:,.2f}")
                                m2.metric("Total Current Value", f"${tot_val:,.2f}")
                                m3.metric("Total Unrealized PnL", f"${tot_pnl:,.2f}", delta=f"{tot_roi:.2f}%")

                                st.dataframe(
                                    df_pnl.style.format({
                                        "Balance": "{:,.4f}",
                                        "Current Price": "${:,.2f}",
                                        "Cost Basis ($)": "${:,.2f}",
                                        "Current Value ($)": "${:,.2f}",
                                        "Unrealized PnL ($)": "${:,.2f}",
                                        "ROI (%)": "{:+.2f}%"
                                    }),
                                    use_container_width=True
                                )

                                # PnL Visualization Bar Chart
                                fig_pnl = px.bar(
                                    df_pnl, 
                                    x="Asset", 
                                    y="Unrealized PnL ($)", 
                                    color="Unrealized PnL ($)",
                                    color_continuous_scale=["red", "grey", "green"],
                                    title="Unrealized PnL by Asset"
                                )
                                st.plotly_chart(fig_pnl, use_container_width=True)
                            else:
                                st.info("No asset data available to compute PnL analytics.")

        except Exception as e:
            st.error(f"Error executing lookup: {str(e)}")