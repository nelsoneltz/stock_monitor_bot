import streamlit as st
import yfinance as yf
import pandas as pd
import asyncio
import threading
import time
from streamlit.runtime.scriptrunner import add_script_run_ctx

# 1. Objeto Global (Fora do contexto do Streamlit)
if "DADOS_GLOBAIS" not in globals():
    globals()["DADOS_GLOBAIS"] = []

st.set_page_config(page_title="YFinance Live", layout="wide")
st.title("📈 Monitoramento com Fila Global")


# 2. WebSocket: Escreve na variável GLOBAL
async def stream_to_global():
    try:
        async with yf.AsyncWebSocket() as ws:
            await ws.subscribe(["AURA33.SA", "PETR4.SA"])
            listener = await ws.listen()
            async for msg in listener:
                symbol = getattr(msg, "symbol", None) or msg.get("symbol")
                price = getattr(msg, "price", None) or msg.get("price")
                if symbol and price:
                    # Alimenta a lista global
                    globals()["DADOS_GLOBAIS"].append(
                        {
                            "Ticker": symbol,
                            "Price": float(price),
                            "Time": pd.Timestamp.now(),
                        }
                    )
                    print(f"📡 Global: {symbol} @ {price}")
    except Exception as e:
        print(f"❌ Erro WS: {e}")


# Inicia a thread se não existir
if "thread_viva" not in st.session_state:
    t = threading.Thread(target=lambda: asyncio.run(stream_to_global()), daemon=True)
    add_script_run_ctx(t)
    t.start()
    st.session_state.thread_viva = True

# 3. Interface: Lê da variável GLOBAL e agrega
placeholder = st.empty()

while True:
    # Coleta o que está na global para a sessão local
    if globals()["DADOS_GLOBAIS"]:
        novos = pd.DataFrame(globals()["DADOS_GLOBAIS"])
        if "df_local" not in st.session_state:
            st.session_state.df_local = novos
        else:
            st.session_state.df_local = pd.concat(
                [st.session_state.df_local, novos]
            ).tail(200)

        # Limpa a global para não processar repetido
        globals()["DADOS_GLOBAIS"] = []

    with placeholder.container():
        if "df_local" in st.session_state and not st.session_state.df_local.empty:
            df = st.session_state.df_local
            df["Time"] = pd.to_datetime(df["Time"])

            # Agregação para o gráfico (Média por minuto)
            df_resampled = (
                df.set_index("Time")
                .groupby("Ticker")
                .resample("1min")["Price"]
                .mean()
                .reset_index()
            )

            # Gráfico
            chart_data = df_resampled.pivot(
                index="Time", columns="Ticker", values="Price"
            )
            st.line_chart(chart_data)

            # Métricas
            cols = st.columns(2)
            for i, ticker in enumerate(["AURA33.SA", "PETR4.SA"]):
                t_val = df[df["Ticker"] == ticker]
                if not t_val.empty:
                    cols[i].metric(ticker, f"R$ {t_val.iloc[-1]['Price']:.2f}")
        else:
            st.info(
                "Aguardando dados... Se o terminal estiver recebendo, aguarde o próximo ciclo."
            )

    time.sleep(5)
    st.rerun()
