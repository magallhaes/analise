import streamlit as st
import pandas as pd
#from login import login
from pathlib import Path
#import locale
from io import BytesIO
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
import streamlit.components.v1 as components
from graficos import (criar_mini_grafico, criar_grafico_top_marcas, criar_grafico_top_linha, criar_grafico_top_grupo)
from chats import (criar_grafico_top_5_vendedores, 
                    criar_grafico_top_5_medicos, 
                    criar_grafico_top_5_parceiros, 
                    criar_grafico_rentabilidade_vendedores,
                    criar_grafico_por_regiao_pie, 
                    criar_grafico_evolucao_vendas_rentabilidade,
                    criar_grafico_por_regiao_pie_rentabilidade
                    )




# Configuração da página do Streamlit
st.set_page_config(
    page_title="Análise de Vendas",
    layout="wide",
    page_icon="assets/images/fav.svg"
)

# Sidebar com logo e filtros
logo = "assets/images/logo.png" # Insira o caminho do seu logo aqui
icon ="assets/images/fav.svg" # Insira o caminho do seu logo aqui
st.logo(logo, icon_image=icon)




# Adicionar o link do CDN do Font Awesome
st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css">', unsafe_allow_html=True)

# Configuração regional para formato brasileiro
#locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para formatar valores em Real
#def formatar_real(valor):
    #return locale.currency(valor, grouping=True, symbol=True)

# Função para formatar valores em Real manualmente
def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
h1 {
            margin-top: -80px;
            margin-bottom: 35px;
            font-size: 48px;
        }
        h3 {
            font-size: 1rem; /* 25px */
        } 
        p {
           font-size: 1rem; /* 3px */ 
        }       
        .card {
            background-color: #f8f9fa;
            padding: 7px;
            border-radius: 6px; /* Valor reduzido */
            box-shadow: 0 4px 20px 1px rgba(0.2, 0, 0, 0.2);
            text-align: center;
            margin-bottom: 35px;
            align-items: center; 
        }
   
        .card img {
            width: 45px;
            height: 35px;
            margin-right: 25px;
            border-radius: 30%;
        }
        .card p { 
            margin: 2px 1px 1px 1px; font-size: 15px; 
            font-weight: bold; color: #003CA6; }    
        .icon {
            font-size: 15px;
            color: #E74E0F;
        }
        .card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 5px;
            background-color: #B2EBF2;
            border-top-left-radius: 8px;
            border-bottom-left-radius: 8px;
        }
        .tabela-responsiva {
            overflow-x: auto;
            margin-bottom: 20px;
            width: 100%;
        }

        .stMarkdown {
        margin-top: -30px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin-bottom: 0px !important;
    }
        .css-1lcbmhc, .css-1d391kg, .css-18e3th9 {
        margin-top: -40px !important;
        margin-bottom: -40px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }    

        .column {
            float: left;
            width: 25%;
            padding: 0 10px;
        }     

        .row:after {
            content: "";
            display: table;
            clear: both;
        }          

        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        @media screen and (max-width: 600px) {
  .column {
    width: 100%;
  }
}  

/* Para telas médias, como tablets */
@media (min-width: 600px) {
    .card p {
        font-size: 12px;
    }
}
            
/* Para telas grandes, como desktops */
@media (min-width: 1024px) {
    .card p {
        font-size: 16px;
    }
}


   .sidebar .sidebar-content { background-color: #003CA6; color: white; }
</style>
""", unsafe_allow_html=True)

# Adicionar filtros na barra lateral
with st.sidebar:
    # Gera a lista de anos, começando com "Todos"
    anos = np.append(["Todos"], df['Ano'].unique())
    
    # Define o índice padrão para o ano de 2023, se estiver presente na lista
    if 2023 in anos:
        index_padrao = list(anos).index(2023)
    else:
        index_padrao = 0  # Se 2023 não estiver na lista, começa com "Todos"
    
    # Filtro de ano
    ano_selecionado = st.selectbox("Ano", anos, index=index_padrao)

    # Filtro de mês (dependente do ano selecionado)
    if ano_selecionado == "Todos":
        meses = np.append(["Todos"], df['Mês'].unique())
    else:
        meses = np.append(["Todos"], df[df['Ano'] == int(ano_selecionado)]['Mês'].unique())
    mes_selecionado = st.selectbox("Mês", meses)

    # Filtro de Região (verificando se existe no DataFrame)
    if 'Região' in df.columns:
        regioes = np.append(["Todos"], df['Região'].unique())
        regiao_selecionada = st.selectbox("Região", regioes)
    else:
        st.warning("A coluna 'Região' não foi encontrada no DataFrame.")

    # Filtro de Marca (verificando se existe no DataFrame)
    if 'Marca' in df.columns:
        marcas = np.append(["Todos"], df['Marca'].unique())
        marca_selecionada = st.selectbox("Marca", marcas)
    else:
        st.warning("A coluna 'Marca' não foi encontrada no DataFrame.")

# Aplicar os filtros automaticamente conforme as seleções
dados_filtrados = df.copy()

if ano_selecionado != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['Ano'] == int(ano_selecionado)]

if mes_selecionado != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['Mês'] == mes_selecionado]

if 'Região' in df.columns and regiao_selecionada != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['Região'] == regiao_selecionada]

if 'Marca' in df.columns and marca_selecionada != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['Marca'] == marca_selecionada]



st.title("Dashboard de Vendas")
# Layout para os cards lado a lado
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

# Calcular métricas
total_vendas = dados_filtrados['Prec_Ven_Total'].sum()
total_imposto = dados_filtrados['R$_Tot_Imposto'].sum()
total_custo = dados_filtrados['Cus_Total'].sum()
total_frete = dados_filtrados['R$_Frete'].sum()
total_despesa = dados_filtrados['R$_Despesa'].sum()
total_comissao = dados_filtrados['R$_Comissao'].sum()
total_incentivo = dados_filtrados['R$_Inc_Venda'].sum()
total_rentabilidade = dados_filtrados['R$_Marg_Contribuicao'].sum()

marg_imposto = (total_imposto / total_vendas) * 100 if total_vendas != 0 else 0
marg_custo = (total_custo / total_vendas) * 100 if total_vendas != 0 else 0
marg_frete = (total_frete / total_vendas) * 100 if total_vendas != 0 else 0
marg_despesa = (total_despesa / total_vendas) * 100 if total_vendas != 0 else 0
marg_comissao = (total_comissao / total_vendas) * 100 if total_vendas != 0 else 0
marg_incentivo = (total_incentivo / total_vendas) * 100 if total_vendas != 0 else 0
marg_rentabilidade = (total_rentabilidade / total_vendas) * 100 if total_vendas != 0 else 0

mini_grafico_base64 = criar_mini_grafico(dados_filtrados)

# Card de Venda total
with col1:
    st.markdown(f"""
    <div class="card">
        <h3><i class="bi bi-cash icon"></i> Total Vendas</h3>
        <p>{formatar_real(total_vendas)}</p>
        <img src="data:image/png;base64,{mini_grafico_base64}" alt="Mini Gráfico" style="margin-top: 10px; width: 50%;;">
    </div>
    """, unsafe_allow_html=True)

# Card de Impostos
with col2:
    st.markdown(f"""
    <div class="card">
        <h3><i class="bi bi-graph-up-arrow icon"></i> Impostos</h3>
        <p style="color:#e60b0b;">-{formatar_real(total_imposto)}</p>
        <p style="font-size: 20px; color: #003CA6;">({marg_imposto:.2f}%)</p>
        <p></p> 

        
    </div>
    """, unsafe_allow_html=True)

#Card de Custo
with col3:
    st.markdown(f"""
    <div class="card">
        <h3><i class="bi bi-wallet2 icon"></i> Custo</h3>
        <p style="color:#e60b0b;">-{formatar_real(total_custo)}</p>
        <p style="font-size: 20px; color: #003CA6;">({marg_custo:.2f}%)</p>
        <p></p>
    </div>
    """, unsafe_allow_html=True) 

# Card de frete
with col4:
    st.markdown(f"""
    <div class="card">
        <h3><i class="bi bi-airplane icon"></i> Frete</h3>
        <p style="color:#e60b0b;">-{formatar_real(total_frete)}</p>
        <p style="font-size: 20px; color: #003CA6;">({marg_frete:.2f}%)</p>
        <p></p>
    </div>
    """, unsafe_allow_html=True) 

# Card de despesas
with col5:
    st.markdown(f"""
    <div class="card">
        <h3><i class="bi bi-clipboard2-data icon"></i> Despesas</h3>
        <p style="color:#e60b0b;">-{formatar_real(total_despesa)}</p>
        <p style="font-size: 20px; color: #003CA6;">({marg_despesa:.2f}%)</p>
        <p></p>
    </div>
    """, unsafe_allow_html=True) 

# Card de Comisao
with col6:
    st.markdown(f"""
    <div class="card">
        <h3><i class="bi bi-diagram-3 icon"></i> Comissão</h3>
        <p style="color:#e60b0b;">-{formatar_real(total_comissao)}</p>
        <p style="font-size: 20px; color: #003CA6;">({marg_comissao:.2f}%)</p>
        <p></p>
    </div>
    """, unsafe_allow_html=True) 

# Card de Incentivo
with col7:
    st.markdown(f"""
    <div class="card">
        <h3><i class="bi bi-file-earmark-bar-graph icon"></i> Incentivo</h3>
        <p style="color:#e60b0b;">-{formatar_real(total_incentivo)}</p>
        <p style="font-size: 20px; color: #003CA6;">({marg_incentivo:.2f}%)</p>
        <p></p>
    </div>
    """, unsafe_allow_html=True) 

# Card de Rentabilidade
with col8:
    st.markdown(f"""
    <div class="card">
        <h3><i class="bi bi-cash-coin icon"></i> Rentabilidade</h3>
        <p>{formatar_real(total_rentabilidade)}</p>
        <p style="font-size: 20px; color: #2ecc71;">({marg_rentabilidade:.2f}%)</p>
        <p></p>
    </div>
    """, unsafe_allow_html=True)

# Linha de gráficos lado a lado
st.markdown("###  ")

# chamar grafico
grafico_col1, grafico_col2, grafico_col3 = st.columns([0.9, 0.5, 0.5])

grafico_venda = criar_grafico_evolucao_vendas_rentabilidade(dados_filtrados)
with grafico_col1:
    st.markdown('<div class="grafico-apex">',unsafe_allow_html=True)
    components.html(grafico_venda, height=500, scrolling=True)  # Reduced height and enabled scrolling
    st.markdown('</div>', unsafe_allow_html=True)


grafico_regiao = criar_grafico_por_regiao_pie(dados_filtrados)
with grafico_col2:
    st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
    components.html(grafico_regiao, height=500, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)
grafico_regiao_retabilidade = criar_grafico_por_regiao_pie_rentabilidade(dados_filtrados)
with grafico_col3:
    st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
    components.html(grafico_regiao_retabilidade, height=500, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)    
      
st.markdown("### ")

col1, col2, col3, col4 = st.columns([0.5, 0.5, 0.5, 0.5])  

# criar_grafico_top_5_vendedores is a function that generates your graph
grafico_vendedores = criar_grafico_top_5_vendedores(dados_filtrados)
with col1:
    st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
    components.html(grafico_vendedores, height=500, scrolling=True)  # Reduced height and enabled scrolling
    st.markdown('</div>', unsafe_allow_html=True)

grafico_rentabilidae = criar_grafico_rentabilidade_vendedores (dados_filtrados) 
with col2:
    st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
    components.html(grafico_rentabilidae, height=500, scrolling=True)  # Reduced height and enabled scrolling
    st.markdown('</div>', unsafe_allow_html=True)  

# grafico de medico is a function that generates your graph
grafico_medico = criar_grafico_top_5_medicos(dados_filtrados)
with col3:
    st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
    components.html(grafico_medico, height=500, scrolling=True)  # Reduced height and enabled scrolling
    st.markdown('</div>', unsafe_allow_html=True)

# Assuming `grafico de parceiro` is a function that generates your graph
grafico_parceiro = criar_grafico_top_5_parceiros(dados_filtrados)
with col4:
    st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
    components.html(grafico_parceiro, height=500, scrolling=True)  # Reduced height and enabled scrolling
    st.markdown('</div>', unsafe_allow_html=True)  


grfcol1, grfcol2, grfcol3 = st.columns([0.8, 0.8, 0.8])

with grfcol1:
    st.markdown('<div style="height:400px; margin-top: -900px;">', unsafe_allow_html=True)
    criar_grafico_top_marcas(dados_filtrados, grfcol1)
    st.markdown('</div>', unsafe_allow_html=True)

with grfcol2:
    st.markdown('<div style="height:400px; margin-top: -400px;">', unsafe_allow_html=True)
    criar_grafico_top_grupo(dados_filtrados, grfcol2)
    st.markdown('</div>', unsafe_allow_html=True)

with grfcol3:
    st.markdown('<div style="height:400px; margin-top: -400px;">', unsafe_allow_html=True)
    criar_grafico_top_linha(dados_filtrados, grfcol3)
    st.markdown('</div>', unsafe_allow_html=True)

# Adicionar o rodapé
footer = """
<style>
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-size: 14px;
        color: #666;
        background-color: #f9f9f9;
        padding: 10px;
    }
</style>
<div class="footer">
    Desenvolvido por Leonardo Magalhães - © 2024
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
