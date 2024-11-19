import streamlit as st
import pandas as pd
import locale
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import streamlit.components.v1 as components



# Configuração do locale para o formato de moeda brasileira
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_real(valor):
    return locale.currency(valor, grouping=True, symbol=True)

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

def criar_grafico_evolucao_vendas_apexcharts(df, coluna):
    if 'Período' in df.columns and 'Prec_Ven_Total' in df.columns and 'R$_Marg_Contribuicao' in df.columns:
        # Convertendo 'Período' para datetime
        df['Período'] = pd.to_datetime(df['Período'], errors='coerce')
        
        # Agrupando e somando os dados
        vendas_por_periodo = df.groupby('Período').agg({
            'Prec_Ven_Total': 'sum',
            'R$_Marg_Contribuicao': 'sum'
        }).reset_index()
        
        # Calculando a porcentagem de rentabilidade para cada período
        vendas_por_periodo['Rentabilidade (%)'] = (
            vendas_por_periodo['R$_Marg_Contribuicao'] / vendas_por_periodo['Prec_Ven_Total'] * 100
        ).fillna(0)  # Preenchendo com 0 se a divisão for inválida

        # Preparando dados para o gráfico
        periodos = vendas_por_periodo['Período'].dt.strftime('%Y-%m-%d').tolist()
        vendas = [venda / 1_000_000 for venda in vendas_por_periodo['Prec_Ven_Total']]  # Convertendo para milhões
        rentabilidade = vendas_por_periodo['Rentabilidade (%)'].tolist()
        
        # Código HTML com ApexCharts embutido
        apex_chart = f"""
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <div id="chart"></div>
        <script>
        var options = {{
            chart: {{
                type: 'line',
                height: 350
            }},
            series: [
                {{
                    name: 'Vendas',
                    type: 'column',
                    data: {vendas}
                }},
                {{
                    name: 'Rentabilidade',
                    type: 'line',
                    data: {rentabilidade}
                }}
            ],
            xaxis: {{
                categories: {periodos},
                title: {{ text: 'Período' }}
            }},
            yaxis: [
                {{
                    title: {{ text: '' }},
                    labels: {{
                        formatter: function(value) {{
                            return "R$: " + value.toFixed(1).toLocaleString('pt-BR') + "M";  // 1 casa decimal, sufixo M
                        }}
                    }}
                }},
                {{
                    opposite: true,
                    title: {{ text: '' }},
                    labels: {{
                        formatter: function(value) {{
                            return value.toFixed(1) + "%";  // 1 casa decimal
                        }}
                    }}
                }}
            ],
            title: {{
                text: 'Evolução de Vendas e Rentabilidade',
                align: 'center'
            }},
            legend: {{
                position: 'top'
            }},
            dataLabels: {{
                enabled: true,
                formatter: function (val, opts) {{
                    if (opts.seriesIndex === 1) {{
                        return val.toFixed(1) + "%";  // Exibe rentabilidade com 1 casa decimal
                    }} else {{
                        return "" ;  // Exibe vendas em milhões com 1 casa decimal
                    }}
                }}
            }}
        }};

        var chart = new ApexCharts(document.querySelector("#chart"), options);
        chart.render();
        </script>
        """
        
        # Renderizando o gráfico usando Streamlit
        st.components.v1.html(apex_chart, height=400)
    else:
        coluna.warning("As colunas 'Período', 'Prec_Ven_Total' ou 'R$_Marg_Contribuicao' não foram encontradas nos dados.")

def criar_grafico_distribuicao_grupo(df, coluna):
    if 'Grupo' in df.columns and 'Prec_Ven_Total' in df.columns:
        venda_total = df['Prec_Ven_Total'].sum()
        df_grupos = df.groupby('Grupo').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        df_top_grupos = df_grupos.nlargest(6, 'Prec_Ven_Total')
        df_restante = df_grupos[~df_grupos['Grupo'].isin(df_top_grupos['Grupo'])]
        
        # Agrupar o restante dos grupos como "Outros"
        outros = pd.DataFrame({'Grupo': ['Outros'], 'Prec_Ven_Total': [df_restante['Prec_Ven_Total'].sum()]})
        df_final = pd.concat([df_top_grupos, outros], ignore_index=True)
        
        # Extrair os rótulos (nomes dos grupos) e valores para o gráfico
        labels = df_final['Grupo'].tolist()
        valores = df_final['Prec_Ven_Total'].tolist()
        
        # Criar o gráfico usando ApexCharts
        html_code = f"""
        <div id="chart-distribuicao-grupo" style="height: 400px;"></div>
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
                text: 'Vendas por Grupo',
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
        var chart = new ApexCharts(document.querySelector("#chart-distribuicao-grupo"), options);
        chart.render();
        </script>
        """
        # Inserir o gráfico dentro da coluna do Streamlit usando um componente HTML
        coluna.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
        components.html(html_code, height=500, scrolling=False)
        coluna.markdown('</div>', unsafe_allow_html=True)
    else:
        coluna.warning("Colunas 'Grupo' ou 'Prec_Ven_Total' não encontradas nos dados.")


def criar_grafico_top_marcas(df, coluna):
    if 'Marca' in df.columns and 'Prec_Ven_Total' in df.columns:
        total_vendas = df['Prec_Ven_Total'].sum()
        top_marcas = df.groupby('Marca').agg({'Prec_Ven_Total': 'sum'}).nlargest(7, 'Prec_Ven_Total').reset_index()
        restante_vendas = total_vendas - top_marcas['Prec_Ven_Total'].sum()
        demais_marcas = pd.DataFrame({'Marca': ['Demais Marcas'], 'Prec_Ven_Total': [restante_vendas]})
        df_final = pd.concat([top_marcas, demais_marcas], ignore_index=True)

        fig = px.bar(df_final, x='Marca', y='Prec_Ven_Total', title="Top vendas por marcas", text='Prec_Ven_Total', color='Marca')
        fig.update_layout(yaxis_title="", xaxis_title="Marca", showlegend=False)
        fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='inside')
        coluna.plotly_chart(fig, use_container_width=True)
    else:
        coluna.warning("Colunas 'Marca' ou 'Prec_Ven_Total' não encontradas nos dados.")

def criar_mini_grafico_evolucao_vendas(df, coluna):
    if 'Período' in df.columns and 'Prec_Ven_Total' in df.columns:
        df['Período'] = pd.to_datetime(df['Período'], errors='coerce')
        vendas_por_periodo = df.groupby('Período').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        fig = go.Figure(go.Scatter(x=vendas_por_periodo['Período'], y=vendas_por_periodo['Prec_Ven_Total'], mode='lines', line=dict(color='#003CA6', width=2)))
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(visible=False), yaxis=dict(visible=False), height=60)
        coluna.plotly_chart(fig, use_container_width=True)
    else:
        coluna.warning("Colunas 'Período' ou 'Prec_Ven_Total' não encontradas nos dados.")

def criar_grafico_vendas_por_vendedor(df, container):
    vendas_por_vendedor = df.groupby('Vendedor')['Prec_Ven_Total'].sum().reset_index()
    fig = px.bar(vendas_por_vendedor, x='Vendedor', y='Prec_Ven_Total', title='Vendas por Vendedor', labels={'Prec_Ven_Total': 'Total de Vendas (R$)'}, color='Vendedor', text='Prec_Ven_Total')
    fig.update_traces(texttemplate='R$ %{y:,.2f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, yaxis_title='Total de Vendas (R$)', xaxis_title='Vendedor')
    container.plotly_chart(fig)

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
        labels = [f"<strong>{vendedor} :: R$ {valor:,.2f}</strong>" for vendedor, valor in zip(top_vendedores['Vendedor'], top_vendedores['Prec_Ven_Total'])]
        valores = top_vendedores['Prec_Ven_Total'].tolist()

        html_code = f"""
        <div id="chart-vendedores" style="height: 400px;"></div>
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
                text: 'Top 5 Vendedores por Vendas',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',
                fontSize: '14px'
            }},
            tooltip: {{
                y: {{
                    formatter: function(value) {{
                        return 'R$ ' + value.toLocaleString('pt-BR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                    }}
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
        var chart = new ApexCharts(document.querySelector("#chart-vendedores"), options);
        chart.render();
        </script>
        """
        return html_code
    else:
        st.warning("Colunas 'Vendedor' ou 'Prec_Ven_Total' não foram encontradas nos dados.")
        return ""



    
#Novo grafico vendedor:

def criar_grafico_distribuicao_vendedor(df, coluna):
    if 'Vendedor' in df.columns and 'Prec_Ven_Total' in df.columns:
        venda_total = df['Prec_Ven_Total'].sum()
        df_vendedor = df.groupby('Vendedor').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        df_top_vendedor = df_vendedor.nlargest(5, 'Prec_Ven_Total')
        df_restante = df_vendedor[~df_vendedor['Vendedor'].isin(df_top_vendedor['Vendedor'])]
        
        # Agrupar o restante dos grupos como "Outros"
        outros = pd.DataFrame({'Vendedor': ['Outros'], 'Prec_Ven_Total': [df_restante['Prec_Ven_Total'].sum()]})
        df_final = pd.concat([df_top_vendedor, outros], ignore_index=True)
        
        # Extrair os rótulos (nomes dos vendedores) e valores para o gráfico
        labels = df_final['Vendedor'].tolist()
        valores = df_final['Prec_Ven_Total'].tolist()
        
        # Criar o gráfico usando ApexCharts
        html_code = f"""
        <div id="chart-distribuicao-grupo" style="height: 400px;"></div>
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
        # Inserir o gráfico dentro da coluna do Streamlit usando um componente HTML
        coluna.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
        components.html(html_code, height=500, scrolling=False)
        coluna.markdown('</div>', unsafe_allow_html=True)
    else:
        coluna.warning("Colunas 'vendedor' ou 'Prec_Ven_Total' não encontradas nos dados.")


def criar_grafico_distribuicao_medicos(df, container, titulo='Distribuição de Vendas por Médico'):
    print(type(container))  # Adicione esta linha para verificar o tipo do objeto
    
    if 'Médico' in df.columns and 'Prec_Ven_Total' in df.columns:
        # Agrupar por médico e somar o total de vendas
        df_medicos = df.groupby('Médico').agg({'Prec_Ven_Total': 'sum'}).reset_index()
        
        # Obter os 5 melhores médicos
        df_top_medicos = df_medicos.nlargest(5, 'Prec_Ven_Total')
        
        # Obter os restantes como "Outros"
        df_restante = df_medicos[~df_medicos['Médico'].isin(df_top_medicos['Médico'])]
        outros = pd.DataFrame({'Médico': ['Outros'], 'Prec_Ven_Total': [df_restante['Prec_Ven_Total'].sum()]})
        
        # Combinar os dados
        df_final = pd.concat([df_top_medicos, outros], ignore_index=True)
        
        # Extrair rótulos e valores para o gráfico
        labels = df_final['Médico'].tolist()
        valores = df_final['Prec_Ven_Total'].tolist()
        
        # Criar o gráfico usando ApexCharts
        html_code = f"""
        <div id="chart-distribuicao-medicos" style="height: 400px;"></div>
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
        var chart = new ApexCharts(document.querySelector("#chart-distribuicao-medicos"), options);
        chart.render();
        </script>
        """
        # Inserir o gráfico dentro da coluna do Streamlit usando um componente HTML
        container.markdown('<div class="grafico-apex">', unsafe_allow_html=True)
        components.html(html_code, height=500, scrolling=False)
        container.markdown('</div>', unsafe_allow_html=True)
    else:
        container.warning("Colunas 'Médico' ou 'Prec_Ven_Total' não encontradas nos dados.")
# novo grafico Médico:

#Grafico linha
def criar_grafico_top_linha(df, coluna):
    if 'Linha' in df.columns and 'Prec_Ven_Total' in df.columns:
        total_vendas = df['Prec_Ven_Total'].sum()
        top_linha = df.groupby('Linha').agg({'Prec_Ven_Total': 'sum'}).nlargest(7, 'Prec_Ven_Total').reset_index()
        restante_vendas = total_vendas - top_linha['Prec_Ven_Total'].sum()
        demais_linha = pd.DataFrame({'Linha': ['Demais Linhas'], 'Prec_Ven_Total': [restante_vendas]})
        df_final = pd.concat([top_linha, demais_linha], ignore_index=True)

        fig = px.bar(df_final, x='Linha', y='Prec_Ven_Total', title="Top vendas por linhas", text='Prec_Ven_Total', color='Linha')
        fig.update_layout(yaxis_title="", xaxis_title="Linha", showlegend=False)
        fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='inside')
        coluna.plotly_chart(fig, use_container_width=True)
    else:
        coluna.warning("Colunas 'Linha' ou 'Prec_Ven_Total' não encontradas nos dados.")

#Grafico grupo

def criar_grafico_top_grupo(df, coluna):
    if 'Grupo' in df.columns and 'Prec_Ven_Total' in df.columns:
        total_vendas = df['Prec_Ven_Total'].sum()
        top_grupo = df.groupby('Grupo').agg({'Prec_Ven_Total': 'sum'}).nlargest(7, 'Prec_Ven_Total').reset_index()
        restante_vendas = total_vendas - top_grupo['Prec_Ven_Total'].sum()
        demais_grupo = pd.DataFrame({'Grupo': ['Demais Grupo'], 'Prec_Ven_Total': [restante_vendas]})
        df_final = pd.concat([top_grupo, demais_grupo], ignore_index=True)

        fig = px.bar(df_final, x='Grupo', y='Prec_Ven_Total', title="Top vendas por grupos", text='Prec_Ven_Total', color='Grupo')
        fig.update_layout(yaxis_title="", xaxis_title="Grupo", showlegend=False)
        fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='inside')
        coluna.plotly_chart(fig, use_container_width=True)
    else:
        coluna.warning("Colunas 'Linha' ou 'Prec_Ven_Total' não encontradas nos dados.")



# Função principal
def main():
    st.title("Análise de Resultados de Vendas")
    df = carregar_dados()
    
    if not df.empty:
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
        
        #criar_grafico_evolucao_vendas(df, col1)
        criar_grafico_evolucao_vendas_apexcharts(df,col1)

        criar_grafico_distribuicao_grupo(df, col2)
        criar_grafico_top_marcas(df, col3)
        criar_mini_grafico_evolucao_vendas(df, col4)
        criar_grafico_vendas_por_vendedor(df, col5)



        grafico_vendedores = criar_grafico_top_5_vendedores(df)
        with col6:
            components.html(grafico_vendedores, height=500)



        grafico_medicos = criar_grafico_apex_tops(df, "Médico", "Top 5 Médicos por Vendas")
        with col7:
            components.html(grafico_medicos, height=500)

        grafico_parceiros = criar_grafico_apex_tops(df, 'Parceiro', 'Top 5 Parceiros')
        with col8:
            components.html(grafico_parceiros, height=500)

        
        grafico_med = criar_grafico_distribuicao_medicos(df, 'Médico', 'Top 5 Médicos')
        with col9:
            components.html(grafico_med , height=500) 

        grafico_vendedor = criar_grafico_distribuicao_vendedor(df)
        with col10:
            components.html(grafico_vendedor, height=500)
        


    else:
        st.warning("Nenhum dado disponível para exibir.")

if __name__ == "__main__":
    main()
