import streamlit as st
import pandas as pd
#import locale
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
from grafico_vendedor import (
    criar_grafico_top_grupos,
    criar_grafico_top_marcas,
    criar_grafico_distribuicao_grupo,
    criar_grafico_vendas_menos_incentivo
)

# Configuração da página do Streamlit, com ícone de página e layout em modo "wide"
st.set_page_config(
    page_title="Análise de Vendas por Vendedor",
    layout="wide",
    page_icon="assets/images/fav.svg"  # Ícone da página no navegador
)

logo = "assets/images/logo.png" # Insira o caminho do seu logo aqui
icon ="assets/images/fav.svg" # Insira o caminho do seu logo aqui
st.logo(logo, icon_image=icon)

# Configuração regional para formato brasileiro
#locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
# Função para formatar valores em Real manualmente
def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
# Função para formatar valores em Real
#def formatar_real(valor):
#    return locale.currency(valor, grouping=True, symbol=True)

# Carregar dados e cachear
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel(r"./db/1. Análise Resultado Vendas_Suplen 2024 v10_1.xlsx", sheet_name="DADOS")
        if 'Período' in df.columns:
            df['Período'] = pd.to_datetime(df['Período'], errors='coerce', dayfirst=True)
            df = df.dropna(subset=['Período'])
        df['Ano'] = df['Período'].dt.year
        df['Mês'] = df['Período'].dt.strftime('%B')
        return df
    except FileNotFoundError:
        st.error("Erro: Planilha não encontrada. Verifique o caminho e o nome do arquivo.")
        return pd.DataFrame()

# Carregar dados
df = carregar_dados()

# CSS personalizado para reduzir o tamanho dos cards
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #FFFFFF;
    border: 1px solid #DCDCDC;
    padding: 5px 15px;
    border-radius: 5px;
    margin-bottom: 10px;
    max-width: 300px;
}

div[data-testid="metric-container"] > div:nth-child(1) {
    font-size: 10px;
}

div[data-testid="metric-container"] > div:nth-child(2) {
    font-size: 16px;  /* Tamanho do título */
}

div[data-testid="metric-container"] > div:last-child {
    font-size: 10px; /* Tamanho do delta (porcentagem) */
}

/* Tamanho dos valores */
div[data-testid="metric-container"] .stMetric-value {
    font-size: 7px;  /* Reduzir o tamanho dos valores aqui */
}

.st-emotion-cache-ekc6ea {
    font-size: 1.0rem;
    color: rgb(0, 0, 0);
    padding-bottom: 0.25rem;                        
            
.st-emotion-cache-p38tq {
    font-size: 1.2rem;
    color: rgb(49, 51, 63);
    padding-bottom: 0.25rem;
}

.st-emotion-cache-jkfxgf p {
    word-break: break-word;
    margin-bottom: 0px;
    font-size: 20px;
}   
.st-emotion-cache-jw45d2 {
    vertical-align: middle;
    overflow: hidden;
    color: inherit;
    fill: currentcolor;
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    font-size: 1.25rem;
    width: 1.25rem;
    height: 1.25rem;
    margin: 0px 0.125rem 0px 0px;
    flex-shrink: 0;
}                                 

</style>
""", unsafe_allow_html=True)

if 'Vendedor' not in df.columns:
    st.error("A coluna 'Vendedor' não foi encontrada na tabela DADOS.")
else:

    # Filtro de Vendedor
    vendedores = df['Vendedor'].unique()
    vendedor_selecionado = st.sidebar.selectbox("Vendedor", vendedores)

    # Filtro de Ano
    anos = np.append(["Todos"], df['Ano'].unique())
    ano_selecionado = st.sidebar.selectbox("Ano", anos)

    # Filtro de Mês
    if ano_selecionado == "Todos":
        meses = np.append(["Todos"], df['Mês'].unique())
    else:
        meses = np.append(["Todos"], df[df['Ano'] == int(ano_selecionado)]['Mês'].unique())
    mes_selecionado = st.sidebar.selectbox("Mês", meses)

    # Aplicar os filtros conforme as seleções
    dados_filtrados = df[df['Vendedor'] == vendedor_selecionado]

    if ano_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['Ano'] == int(ano_selecionado)]

    if mes_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['Mês'] == mes_selecionado]

    # Layout de colunas para métricas e gráficos
    col_cards1, col_cards2, col_grafico, col_grafico2 = st.columns([0.5, 0.5, 0.9, 0.9])

    def calcular_total_geral(df, ano_selecionado):
        if ano_selecionado == "Todos":
            return df['Prec_Ven_Total'].sum()
        else:
         dados_filtrados_ano = df[df['Ano'] == int(ano_selecionado)]
        return dados_filtrados_ano['Prec_Ven_Total'].sum()

    with col_cards1:
        tot_vendas = calcular_total_geral(df, ano_selecionado)
        st.metric(label="Total Geral", value=formatar_real(tot_vendas))
    
    
    with col_cards2:
        total_vendas = dados_filtrados['Prec_Ven_Total'].sum()
        total_incentivo = dados_filtrados['R$_Inc_Venda'].sum()
        rentabilidade = dados_filtrados['R$_Marg_Contribuicao'].sum()
        marg_Incentivo = (total_incentivo / total_vendas) * 100 if total_vendas != 0 else 0
        marg_Rentabilidade = (rentabilidade / total_vendas) * 100 if total_vendas != 0 else 0

        st.metric(label="Total Vendas do Vendedor", value=formatar_real(total_vendas))
        st.metric(label="Incentivo", value=formatar_real(total_incentivo), delta=f"{marg_Incentivo:.2f}%")
        st.metric(label="Rentabilidade", value=formatar_real(rentabilidade), delta=f"{marg_Rentabilidade:.2f}%")
        style_metric_cards()

    with col_grafico:
        # Gráfico de Top Marcas
        grafico_top_marcas = criar_grafico_top_marcas(dados_filtrados, coluna='Marca')
        if grafico_top_marcas:
            st.plotly_chart(grafico_top_marcas, use_container_width=True)
    with col_grafico2:
        # Gráfico de Top grupo
        grafico_top_grup = criar_grafico_top_grupos(dados_filtrados)
        if grafico_top_marcas:
            st.plotly_chart(grafico_top_grup, use_container_width=True)        

    # Exibir outros gráficos abaixo dos resumos
    #st.markdown("### Distribuição de Vendas por Grupo")
    grafico_distribuicao_grupo = criar_grafico_distribuicao_grupo(dados_filtrados, coluna='Grupo')
    if grafico_distribuicao_grupo:
        st.plotly_chart(grafico_distribuicao_grupo)

    # Gráfico de produtos com mais vendas e menos incentivo
    #st.markdown("### Produtos com Maior Vendas e Menor Incentivo")
    grafico_vendas_menos_incentivo = criar_grafico_vendas_menos_incentivo(dados_filtrados)
    if grafico_vendas_menos_incentivo:
        st.plotly_chart(grafico_vendas_menos_incentivo, use_container_width=True)

    # Tabela de detalhamento das vendas por Parceiro
    st.markdown("### Detalhamento das vendas por Parceiro:")
    detalhamento_parceiro = dados_filtrados.groupby('Parceiro').agg({
        'Prec_Ven_Total': 'sum',
        'R$_Inc_Venda': 'sum'
    }).reset_index()
    st.table(detalhamento_parceiro[['Parceiro', 'Prec_Ven_Total', 'R$_Inc_Venda']].sort_values(by='Prec_Ven_Total', ascending=False))
