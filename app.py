import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Investidor Pro Dashboard", layout="wide")

# Lista de ativos (Ticker: [Quantidade, Alvo %])
# Ativos brasileiros precisam do .SA no final
meus_ativos = {
    'ITUB3.SA': [920, 15],  # Exemplo baseado no seu saldo em Itaú
    'GOAU4.SA': [800, 10],  # Metalurgia Gerdau
    'IAUM': [260, 15],      # iShares Gold Trust Micro
    'SCHD': [60, 15],       # Schwab US Dividend Equity
    'STAG': [80, 15],       # STAG Industrial
    'BTC-USD': [0.01, 10],  # Bitcoin (Placeholder para sua carteira Cripto)
    'ETH-USD': [0.1, 5],    # Ethereum
    'SCHV': [40, 5],        # Schwab US Large-Cap Value
    'DUHP': [30, 5],        # Dimensional US High Profitability
    'JEPQ': [15, 5]         # JPMorgan Nasdaq Equity Premium
}

@st.cache_data(ttl=3600)
def buscar_dados():
    tickers = list(meus_ativos.keys())
    # Adicionamos o câmbio para converter tudo para Real
    tickers.append('USDBRL=X')
    df = yf.download(tickers, period="1d")['Adj Close'].iloc[-1]
    return df

st.title("🚀 Gestor de Patrimônio Inteligente")

try:
    precos = buscar_dados()
    dolar = precos['USDBRL=X']
    
    dados_totais = []
    patrimonio_brl = 0

    for ticker, info in meus_ativos.items():
        qtd, alvo = info
        preco_atual = precos[ticker]
        
        # Converte para BRL se for ativo americano ou cripto (em USD)
        if ".SA" not in ticker:
            valor_brl = qtd * preco_atual * dolar
            moeda = "USD"
        else:
            valor_brl = qtd * preco_atual
            moeda = "BRL"
            
        patrimonio_brl += valor_brl
        dados_totais.append([ticker, qtd, preco_atual, valor_brl, alvo, moeda])

    df = pd.DataFrame(dados_totais, columns=['Ativo', 'Qtd', 'Preço Unit.', 'Total (R$)', 'Alvo %', 'Moeda'])
    df['Atual %'] = (df['Total (R$)'] / patrimonio_brl) * 100
    df['Desvio'] = df['Atual %'] - df['Alvo %']

    # Indicadores de Decisão
    st.metric("Patrimônio Total", f"R$ {patrimonio_brl:,.2f}")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Distribuição da Carteira")
        fig = px.pie(df, values='Total (R$)', names='Ativo', hole=0.5)
        st.plotly_chart(fig)

    with col2:
        st.subheader("Sugestão de Compra/Venda")
        def sinalizar(d):
            if d < -2: return "🟢 COMPRAR"
            if d > 2: return "🔴 EXPOSTO (AGUARDAR)"
            return "🟡 EQUILIBRADO"
        
        df['Ação'] = df['Desvio'].apply(sinalizar)
        st.dataframe(df[['Ativo', 'Atual %', 'Alvo %', 'Ação']].style.format({'Atual %': '{:.2f}%', 'Alvo %': '{:.2f}%'}))

except Exception as e:
    st.error("Erro ao carregar dados. Verifique a conexão ou os tickers.")
