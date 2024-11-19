import streamlit as st
import pandas as pd
import locale
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import json  # Importação necessária
import io
import base64
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Análise de Vendas", 
    layout="wide",
    page_icon="assets/images/fav.svg",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_real(valor):
    return locale.currency(valor, grouping=True, symbol=True)

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel(r"./db/1. Análise Resultado Vendas_Suplen 2024 v09.xlsm", sheet_name="DADOS")
        return df
    except FileNotFoundError:
        st.error("Erro: Planilha não encontrada. Verifique o caminho e o nome do arquivo.")
        return pd.DataFrame()
    

def criar_grafico_evolucao_vendas_apexcharts(df):
    if 'Período' in df.columns and 'Prec_Ven_Total' in df.columns and 'R$_Marg_Contribuicao' in df.columns:
        df['Período'] = pd.to_datetime(df['Período'], errors='coerce')
        vendas_por_periodo = df.groupby('Período').agg({
            'Prec_Ven_Total': 'sum',
            'R$_Marg_Contribuicao': 'sum'
        }).reset_index()
        
        vendas_por_periodo['Rentabilidade (%)'] = (
            vendas_por_periodo['R$_Marg_Contribuicao'] / vendas_por_periodo['Prec_Ven_Total'] * 100
        ).fillna(0)

        periodos = vendas_por_periodo['Período'].dt.strftime('%Y-%m-%d').tolist()
        vendas = [venda / 1_000_000 for venda in vendas_por_periodo['Prec_Ven_Total']]
        rentabilidade = vendas_por_periodo['Rentabilidade (%)'].tolist()
        
        apex_chart = f"""
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <div id="chart-evolucao-vendas"></div>
        <script>
        var options = {{
            chart: {{ type: 'line', height: 350 }},
            series: [
                {{ name: 'Vendas (R$ milhões)', type: 'column', data: {vendas} }},
                {{ name: 'Rentabilidade (%)', type: 'line', data: {rentabilidade} }}
            ],
            xaxis: {{ categories: {periodos}, title: {{ text: 'Período' }} }},
            yaxis: [
                {{
                    title: {{ text: 'Vendas (R$ milhões)' }},
                    labels: {{
                        formatter: function(value) {{ return "R$ " + value.toFixed(1).toLocaleString('pt-BR') + "M"; }}
                    }}
                }},
                {{
                    opposite: true,
                    title: {{ text: 'Rentabilidade (%)' }},
                    labels: {{
                        formatter: function(value) {{ return value.toFixed(1) + "%"; }}
                    }}
                }}
            ],
            title: {{ text: 'Evolução de Vendas e Rentabilidade (%)', align: 'center' }},
            legend: {{ position: 'top' }},
            dataLabels: {{
                enabled: true,
                formatter: function (val, opts) {{
                    return opts.seriesIndex === 1 ? val.toFixed(1) + "%" : "R$ " + val.toFixed(1) + "M";
                }}
            }}
        }};
        var chart = new ApexCharts(document.querySelector("#chart-evolucao-vendas"), options);
        chart.render();
        </script>
        """
        
        st.components.v1.html(apex_chart, height=400)
    else:
        st.warning("As colunas 'Período', 'Prec_Ven_Total' ou 'R$_Marg_Contribuicao' não foram encontradas nos dados.")

def criar_grafico_distribuicao_grupo(df):
    if 'Grupo' in df.columns and 'Prec_Ven_Total' in df.columns:
        venda_total = df['Prec_Ven_Total'].sum()
        df_grupos = df.groupby('Grupo').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        df_top_grupos = df_grupos.nlargest(6, 'Prec_Ven_Total')
        df_restante = df_grupos[~df_grupos['Grupo'].isin(df_top_grupos['Grupo'])]
        
        outros = pd.DataFrame({'Grupo': ['Outros'], 'Prec_Ven_Total': [df_restante['Prec_Ven_Total'].sum()]})
        df_final = pd.concat([df_top_grupos, outros], ignore_index=True)
        
        labels = df_final['Grupo'].tolist()
        valores = df_final['Prec_Ven_Total'].tolist()
        
        html_code = f"""
        <div id="chart-distribuicao-grupo" style="height: 400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{ type: 'pie', width: '100%', height: '400px' }},
            series: {valores},
            labels: {labels},
            title: {{ text: 'Vendas por Grupo', align: 'center' }},
            legend: {{ position: 'bottom', fontSize: '14px' }},
            dataLabels: {{
                enabled: true,
                formatter: function (val) {{ return val.toFixed(2) + '%'; }},
                style: {{ fontSize: '14px', colors: ["#304758"] }}
            }},
            responsive: [{{
                breakpoint: 480,
                options: {{
                    chart: {{ width: 300 }},
                    legend: {{ position: 'bottom', fontSize: '12px' }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-distribuicao-grupo"), options);
        chart.render();
        </script>
        """
        st.components.v1.html(html_code, height=500)
    else:
        st.warning("Colunas 'Grupo' ou 'Prec_Ven_Total' não encontradas nos dados.")

def criar_grafico_top_marcas(df):
    if 'Marca' in df.columns and 'Prec_Ven_Total' in df.columns:
        total_vendas = df['Prec_Ven_Total'].sum()
        top_marcas = df.groupby('Marca').agg({'Prec_Ven_Total': 'sum'}).nlargest(7, 'Prec_Ven_Total').reset_index()
        restante_vendas = total_vendas - top_marcas['Prec_Ven_Total'].sum()
        demais_marcas = pd.DataFrame({'Marca': ['Demais Marcas'], 'Prec_Ven_Total': [restante_vendas]})
        df_final = pd.concat([top_marcas, demais_marcas], ignore_index=True)

        fig = px.bar(df_final, x='Marca', y='Prec_Ven_Total', title="Top 7 Marcas por Vendas", text='Prec_Ven_Total', color='Marca')
        fig.update_layout(yaxis_title="Vendas (R$)", xaxis_title="Marca", showlegend=False)
        fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Colunas 'Marca' ou 'Prec_Ven_Total' não encontradas nos dados.")

def criar_mini_grafico_evolucao_vendas(df):
    if 'Período' in df.columns and 'Prec_Ven_Total' in df.columns:
        df['Período'] = pd.to_datetime(df['Período'], errors='coerce')
        vendas_por_periodo = df.groupby('Período').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        fig = go.Figure(go.Scatter(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Prec_Ven_Total'], mode='lines', line=dict(color='#003CA6', width=2)))
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(visible=False), yaxis=dict(visible=False), height=60)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Colunas 'Período' ou 'Prec_Ven_Total' não encontradas nos dados.")

def criar_grafico_vendas_por_vendedor(df):
    vendas_por_vendedor = df.groupby('Vendedor')['Prec_Ven_Total'].sum().reset_index()
    fig = px.bar(vendas_por_vendedor, x='Vendedor', y='Prec_Ven_Total', title='Vendas por Vendedor', labels={'Prec_Ven_Total': 'Total de Vendas (R$)'}, color='Vendedor', text='Prec_Ven_Total')
    fig.update_traces(texttemplate='R$ %{y:,.2f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, yaxis_title='Total de Vendas (R$)', xaxis_title='Vendedor')
    st.plotly_chart(fig)

def criar_mini_grafico(df):
    vendas_por_periodo = df.groupby('Período')['Prec_Ven_Total'].sum()
    fig, ax = plt.subplots(figsize=(3, 1))
    ax.plot(vendas_por_periodo.index, vendas_por_periodo.values, color='#003CA6')
    ax.fill_between(vendas_por_periodo.index, vendas_por_periodo.values, color='#003CA6', alpha=0.3)
    ax.set_axis_off()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64            

def criar_grafico_apex_tops(df, categoria, titulo):
    if categoria in df.columns and 'Prec_Ven_Total' in df.columns:
        vendas_categoria = df.groupby(categoria)['Prec_Ven_Total'].sum().reset_index()
        top_categoria = vendas_categoria.nlargest(5, 'Prec_Ven_Total')
        labels = top_categoria[categoria].tolist()
        valores = top_categoria['Prec_Ven_Total'].tolist()

        html_code = f"""
        <div id="chart-{categoria}" style="height: 400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'pie',
                width: '100%',
                height: '400px'
            }},
            series: {valores},
            labels: {labels},
            title: {{
                text: '{titulo}',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',  // Legenda abaixo do gráfico
                fontSize: '14px'     // Tamanho da fonte da legenda
            }},
            responsive: [{{
                breakpoint: 480,
                options: {{
                    chart: {{
                        width: 300
                    }},
                    legend: {{
                        position: 'bottom',
                        fontSize: '12px'   // Tamanho da fonte ajustado para dispositivos menores
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-{categoria}"), options);
        chart.render();
        </script>
        """
        return html_code
    else:
        st.warning(f"Coluna '{categoria}' não encontrada nos dados.")
        return ""
    
def criar_grafico_top_5_vendedores(df):

    if 'Vendedor' in df.columns and 'Prec_Ven_Total' in df.columns:
        vendas_vendedor = df.groupby('Vendedor')['Prec_Ven_Total'].sum().reset_index()
        top_vendedores = vendas_vendedor.nlargest(5, 'Prec_Ven_Total')
        labels = top_vendedores['Vendedor'].tolist()
        valores = top_vendedores['Prec_Ven_Total'].tolist()

        html_code = f"""
        <div id="chart-vendedores" style="height: 400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'donut',  // Mudança para gráfico de pizza
                width: '100%',
                height: '400px'
            }},
            series: {valores},  // Valores correspondentes
            labels: {labels},  // Etiquetas correspondentes aos vendedores
            title: {{
                text: 'Top 5 Vendedores por Vendas',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',  // Legenda abaixo do gráfico
                fontSize: '14px'     // Ajuste de fonte
            }},

            tooltip: {{
                y: {{
                    formatter: function(value) {{
                        return 'R$ ' + value.toLocaleString('pt-BR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                    }}
                }}
            }},

            dataLabels: {{
                enabled: true,
                formatter: function (val) {{
                    return val.toFixed(2) + '%';  // Exibir valores como porcentagem com 2 casas decimais
                }},
                style: {{
                    fontSize: '14px',
                    colors: ["#304758"]
                }}
            }},
            responsive: [{{
                breakpoint: 480,
                options: {{
                    chart: {{
                        width: 300
                    }},
                    legend: {{
                        position: 'bottom',
                        fontSize: '12px'  // Tamanho ajustado para dispositivos menores
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-vendedores"), options);
        chart.render();
        </script>
        """
        return html_code
    else:
        st.warning("Colunas 'Vendedor' ou 'Prec_Ven_Total' não foram encontradas nos dados.")
        return ""   


def criar_grafico_distribuicao_vendedor(df, coluna="Vendedor"):
    if 'Vendedor' in df.columns and 'Prec_Ven_Total' in df.columns:
        venda_total = df['Prec_Ven_Total'].sum()
        df_vendedor = df.groupby('Vendedor').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        df_top_vendedor = df_vendedor.nlargest(6, 'Prec_Ven_Total')
        df_restante = df_vendedor[~df_vendedor['Vendedor'].isin(df_top_vendedor['Vendedor'])]
        
        # Agrupar o restante dos grupos como "Outros"
        outros = pd.DataFrame({'Vendedor': ['Outros'], 'Prec_Ven_Total': [df_restante['Prec_Ven_Total'].sum()]})
        df_final = pd.concat([df_top_vendedor, outros], ignore_index=True)
        
        # Extrair os rótulos (nomes dos vendedores) e valores para o gráfico
        labels = json.dumps(df_final['Vendedor'].tolist())  # JSON para uso no JS
        valores = df_final['Prec_Ven_Total'].tolist()
        
        # Criar o gráfico usando ApexCharts
        html_code = f"""
        <div id="chart-distribuicao-vendedor" style="height: 400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'pie',
                width: '100%',
                height: '400px'
            }},
            series: {valores},
            labels: {labels},
            title: {{
                text: 'Vendas por Vendedor',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',
                fontSize: '14px'
            }},
            dataLabels: {{
                enabled: true,
                formatter: function (val) {{
                    return val.toFixed(2) + '%';  // Exibir valores como porcentagem com 2 casas decimais
                }},
                style: {{
                    fontSize: '14px',
                    colors: ["#304758"]
                }}
            }},
            responsive: [{{
                breakpoint: 480,
                options: {{
                    chart: {{
                        width: 300
                    }},
                    legend: {{
                        position: 'bottom',
                        fontSize: '12px'
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-distribuicao-vendedor"), options);
        chart.render();
        </script>
        """
        
        # Inserir o gráfico dentro do Streamlit usando um componente HTML
        st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
        components.html(html_code, height=500, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Colunas 'Vendedor' ou 'Prec_Ven_Total' não encontradas nos dados.")

def criar_grafico_distribuicao_medico(df, coluna="Médico"):
    if 'Médico' in df.columns and 'Prec_Ven_Total' in df.columns:
        venda_total = df['Prec_Ven_Total'].sum()
        df_medico = df.groupby('Médico').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        df_top_medico = df_medico.nlargest(5, 'Prec_Ven_Total')
        df_restante = df_medico[~df_medico['Médico'].isin(df_top_medico['Médico'])]
        
        # Agrupar o restante dos grupos como "Outros"
        outros = pd.DataFrame({'Médico': ['Outros'], 'Prec_Ven_Total': [df_restante['Prec_Ven_Total'].sum()]})
        df_final = pd.concat([df_top_medico, outros], ignore_index=True)
        
        # Extrair os rótulos (nomes dos Medicos) e valores para o gráfico
        labels = json.dumps(df_final['Médico'].tolist())  # JSON para uso no JS
        valores = df_final['Prec_Ven_Total'].tolist()
        
        # Criar o gráfico usando ApexCharts
        html_code = f"""
        <div id="chart-distribuicao-medico" style="height: 400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'donut',
                width: '100%',
                height: '400px'
            }},
            series: {valores},
            labels: {labels},
            title: {{
                text: 'Vendas por Médico',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',
                fontSize: '14px'
            }},
            dataLabels: {{
                enabled: true,
                formatter: function (val) {{
                    return val.toFixed(2) + '%';  // Exibir valores como porcentagem com 2 casas decimais
                }},
                style: {{
                    fontSize: '14px',
                    colors: ["#304758"]
                }}
            }},
            responsive: [{{
                breakpoint: 480,
                options: {{
                    chart: {{
                        width: 300
                    }},
                    legend: {{
                        position: 'bottom',
                        fontSize: '12px'
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-distribuicao-medico"), options);
        chart.render();
        </script>
        """
        
        # Inserir o gráfico dentro do Streamlit usando um componente HTML
        st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
        components.html(html_code, height=500, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Colunas 'Médico' ou 'Prec_Ven_Total' não encontradas nos dados.")

def criar_grafico_distribuicao_parceiro(df, coluna="Parceiro"):
    if 'Parceiro' in df.columns and 'Prec_Ven_Total' in df.columns:
        venda_total = df['Prec_Ven_Total'].sum()
        df_parceiro = df.groupby('Parceiro').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        df_top_parceiro = df_parceiro.nlargest(5, 'Prec_Ven_Total')
        df_restante = df_parceiro[~df_parceiro['Parceiro'].isin(df_top_parceiro['Parceiro'])]
        
        # Agrupar o restante dos grupos como "Outros"
        outros = pd.DataFrame({'Parceiro': ['Outros'], 'Prec_Ven_Total': [df_restante['Prec_Ven_Total'].sum()]})
        df_final = pd.concat([df_top_parceiro, outros], ignore_index=True)
        
        # Extrair os rótulos (nomes dos parceiro) e valores para o gráfico
        labels = json.dumps(df_final['Parceiro'].tolist())  # JSON para uso no JS
        valores = df_final['Prec_Ven_Total'].tolist()
        
        # Criar o gráfico usando ApexCharts
        html_code = f"""
        <div id="chart-distribuicao-parceiro" style="height: 400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'pie',
                width: '100%',
                height: '400px'
            }},
            series: {valores},
            labels: {labels},
            title: {{
                text: 'Vendas por Parceiro',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',
                fontSize: '14px'
            }},
            dataLabels: {{
                enabled: true,
                formatter: function (val) {{
                    return val.toFixed(2) + '%';  // Exibir valores como porcentagem com 2 casas decimais
                }},
                style: {{
                    fontSize: '14px',
                    colors: ["#304758"]
                }}
            }},
            responsive: [{{
                breakpoint: 480,
                options: {{
                    chart: {{
                        width: 300
                    }},
                    legend: {{
                        position: 'bottom',
                        fontSize: '12px'
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-distribuicao-parceiro"), options);
        chart.render();
        </script>
        """
        
        # Inserir o gráfico dentro do Streamlit usando um componente HTML
        st.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
        components.html(html_code, height=500, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Colunas 'Médico' ou 'Prec_Ven_Total' não encontradas nos dados.")

# Carregar e exibir dados
df = carregar_dados()

# Exibir gráficos um abaixo do outro
with st.container():
    st.header("Evolução de Vendas e Rentabilidade")
    criar_grafico_evolucao_vendas_apexcharts(df)

with st.container():
    st.header("Distribuição de Vendas por Grupo")
    criar_grafico_distribuicao_grupo(df)

with st.container():
    st.header("Top 7 Marcas por Vendas")
    criar_grafico_top_marcas(df)

with st.container():
    st.header("Vendas por Vendedor")
    criar_grafico_vendas_por_vendedor(df)  

with st.container():
    st.header("Mini grafico")
    criar_mini_grafico(df)

with st.container():
    st.header("Gráfico Apex Top")
    criar_grafico_apex_tops(df, categoria="Vendedor", titulo="Top Vendas por Categoria")

with st.container():
    st.header("top 5 vendedores")
    criar_grafico_top_5_vendedores(df)

with st.container():
    st.header("top 5 vendedores")
    criar_grafico_distribuicao_vendedor(df, coluna="Vendedor")

with st.container():
    st.header("top 5 Médicos")
    criar_grafico_distribuicao_medico(df, coluna="Médico")

with st.container():
    st.header("Top Parceiros")
criar_grafico_distribuicao_parceiro(df, coluna="Parceiro")      
