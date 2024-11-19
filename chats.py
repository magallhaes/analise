# grafico_vendedores.py
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.graph_objects as go
import base64
from io import BytesIO

# grafico vendedor
def criar_grafico_top_5_vendedores(dados_filtrados):
    if 'Vendedor' in dados_filtrados.columns and 'Prec_Ven_Total' in dados_filtrados.columns:
        # Group by 'Vendedor' and calculate the total sales
        vendas_vendedor = dados_filtrados.groupby('Vendedor')['Prec_Ven_Total'].sum().reset_index()

        # Sort by total sales and select the top 5
        top_vendedores = vendas_vendedor.nlargest(5, 'Prec_Ven_Total')
        
        # Get the total sales of the others (the ones not in the top 5)
        outros_vendedores = vendas_vendedor[~vendas_vendedor['Vendedor'].isin(top_vendedores['Vendedor'])]
        total_outros = outros_vendedores['Prec_Ven_Total'].sum()

        # Create a new DataFrame for the "Outros" category
        outros = pd.DataFrame({'Vendedor': ['Outros'], 'Prec_Ven_Total': [total_outros]})

        # Concatenate the "Outros" category with the top vendors
        top_vendedores = pd.concat([top_vendedores, outros], ignore_index=True)

        # Create labels and values for the chart
        labels = [f"<strong>{vendedor} : R$ {valor:,.2f}</strong>" for vendedor, valor in zip(top_vendedores['Vendedor'], top_vendedores['Prec_Ven_Total'])]
        valores = top_vendedores['Prec_Ven_Total'].tolist()

        # Generate the HTML and JavaScript for the chart
        html_code = f"""
        <div id="chart-vendedores" style="height: 300px;"></div>
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
                text: 'Top 5 Vendedores',
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
                        horizontalAlign: 'left',
                        fontSize: '10px'
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
        return "Colunas 'Vendedor' ou 'Prec_Ven_Total' não encontradas nos dados."

# grafico rentabilidade
def criar_grafico_rentabilidade_vendedores(dados_filtrados):
    if 'Vendedor' in dados_filtrados.columns and 'R$_Marg_Contribuicao' in dados_filtrados.columns:
        # Group by 'Vendedor' and calculate the total sales
        vendas_vendedor = dados_filtrados.groupby('Vendedor')['R$_Marg_Contribuicao'].sum().reset_index()

        # Sort by total sales and select the top 5
        top_vendedores = vendas_vendedor.nlargest(5, 'R$_Marg_Contribuicao')
        
        # Get the total sales of the others (the ones not in the top 5)
        outros_vendedores = vendas_vendedor[~vendas_vendedor['Vendedor'].isin(top_vendedores['Vendedor'])]
        total_outros = outros_vendedores['R$_Marg_Contribuicao'].sum()

        # Create a new DataFrame for the "Outros" category
        outros = pd.DataFrame({'Vendedor': ['Outros'], 'R$_Marg_Contribuicao': [total_outros]})

        # Concatenate the "Outros" category with the top vendors
        top_vendedores = pd.concat([top_vendedores, outros], ignore_index=True)

        # Create labels and values for the chart
        labels = [f"<strong>{vendedor} : R$ {valor:,.2f}</strong>" for vendedor, valor in zip(top_vendedores['Vendedor'], top_vendedores['R$_Marg_Contribuicao'])]
        valores = top_vendedores['R$_Marg_Contribuicao'].tolist()

        # Generate the HTML and JavaScript for the chart
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
                text: 'Rentabilidade',
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
                        horizontalAlign: 'left',
                        fontSize: '10px'
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
        return "Colunas 'Vendedor' ou 'R$_Marg_Contribuicao' não encontradas nos dados."

# Grafico de médico
def criar_grafico_top_5_medicos(dados_filtrados):
    if 'Médico' in dados_filtrados.columns and 'Prec_Ven_Total' in dados_filtrados.columns:
        # Agrupar por 'Médico' e calcular o total de vendas
        vendas_medico = dados_filtrados.groupby('Médico')['Prec_Ven_Total'].sum().reset_index()

        # Ordenar pelas maiores vendas e selecionar os 5 primeiros
        top_medicos = vendas_medico.nlargest(5, 'Prec_Ven_Total')

        # Obter as vendas totais dos demais (os que não estão no top 5)
        outros_medicos = vendas_medico[~vendas_medico['Médico'].isin(top_medicos['Médico'])]
        total_outros = outros_medicos['Prec_Ven_Total'].sum()

        # Criar um novo DataFrame para a categoria "Outros"
        outros = pd.DataFrame({'Médico': ['Outros'], 'Prec_Ven_Total': [total_outros]})

        # Concatenar a categoria "Outros" com os 5 melhores médicos
        top_medicos = pd.concat([top_medicos, outros], ignore_index=True)

        # Criar rótulos e valores para o gráfico
        labels = [f"<strong>{medico} : R$ {valor:,.2f}</strong>" for medico, valor in zip(top_medicos['Médico'], top_medicos['Prec_Ven_Total'])]
        valores = top_medicos['Prec_Ven_Total'].tolist()

        # Gerar o código HTML e JavaScript para o gráfico
        html_code = f"""
        <div id="chart-medicos" style="height: 100%; width: 100%;"></div>
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
                text: 'Top 5 Médicos',
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
                        horizontalAlign: 'left',
                        fontSize: '10px'
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-medicos"), options);
        chart.render();
        </script>
        """
        return html_code
    else:
        return "Colunas 'Médico' ou 'Prec_Ven_Total' não encontradas nos dados."


# Gráfico de parceiro
def criar_grafico_top_5_parceiros(dados_filtrados):
    if 'Parceiro' in dados_filtrados.columns and 'Prec_Ven_Total' in dados_filtrados.columns:
        # Agrupar por 'Parceiro' e calcular o total de vendas
        vendas_parceiro = dados_filtrados.groupby('Parceiro')['Prec_Ven_Total'].sum().reset_index()

        # Ordenar pelas maiores vendas e selecionar os 5 primeiros
        top_parceiros = vendas_parceiro.nlargest(5, 'Prec_Ven_Total')

        # Obter as vendas totais dos demais (os que não estão no top 5)
        outros_parceiros = vendas_parceiro[~vendas_parceiro['Parceiro'].isin(top_parceiros['Parceiro'])]
        total_outros = outros_parceiros['Prec_Ven_Total'].sum()

        # Criar um novo DataFrame para a categoria "Outros"
        outros = pd.DataFrame({'Parceiro': ['Outros'], 'Prec_Ven_Total': [total_outros]})

        # Concatenar a categoria "Outros" com os 5 melhores parceiros
        top_parceiros = pd.concat([top_parceiros, outros], ignore_index=True)

        # Criar rótulos e valores para o gráfico
        labels = [f"<strong>{parceiro} : R$ {valor:,.2f}</strong>" for parceiro, valor in zip(top_parceiros['Parceiro'], top_parceiros['Prec_Ven_Total'])]
        valores = top_parceiros['Prec_Ven_Total'].tolist()

        # Gerar o código HTML e JavaScript para o gráfico
        html_code = f"""
        <div id="chart-parceiros" style="height: 400px;"></div>
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
                text: 'Top 5 Parceiros',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',  // Manter a legenda na parte de baixo
                fontSize: '14px',
                horizontalAlign: 'left',  // Alinha os itens da legenda à esquerda
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
                        horizontalAlign: 'left',  // Também manter alinhado à esquerda em dispositivos móveis
                        fontSize: '10px'
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-parceiros"), options);
        chart.render();
        </script>
        """
        return html_code
    else:
        return "Colunas 'Parceiro' ou 'Prec_Ven_Total' não encontradas nos dados."


# grafico de venda por região
def criar_grafico_por_regiao_pie(dados_filtrados):
    if 'Região' in dados_filtrados.columns and 'Prec_Ven_Total' in dados_filtrados.columns:
        # Agrupar por 'Região' e calcular o total de vendas
        vendas_regiao = dados_filtrados.groupby('Região')['Prec_Ven_Total'].sum().reset_index()

        # Criar rótulos e valores para o gráfico
        labels = [f"<strong>{regiao} : R$ {valor:,.2f}</strong>" for regiao, valor in zip(vendas_regiao['Região'], vendas_regiao['Prec_Ven_Total'])]
        valores = vendas_regiao['Prec_Ven_Total'].tolist()

        # Gerar o código HTML e JavaScript para o gráfico
        html_code = f"""
        <div id="chart-regiao" style="height: 100%; width: 100%;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'pie',
                height: '100%',  // Ajuste automático de altura
                width: '100%',   // Ajuste automático de largura
            }},
            series: {valores},
            labels: {labels},
            title: {{
                text: 'Vendas por Região',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',
                fontSize: '12px',
                horizontalAlign: 'left'  // Centraliza os itens da legenda
            }},
            tooltip: {{
                y: {{
                    formatter: function(value) {{
                        return 'R$ ' + value.toLocaleString('pt-BR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                    }}
                }}
            }},
            responsive: [{{
                breakpoint: 768,
                options: {{
                    chart: {{
                        height: '400px'  // Para tablets e dispositivos menores
                    }},
                    legend: {{
                        fontSize: '10px'  // Fonte menor em dispositivos menores
                    }}
                }}
            }}, {{
                breakpoint: 480,
                options: {{
                    chart: {{
                        height: '300px'  // Para telas pequenas
                    }},
                    legend: {{
                        fontSize: '9px',  // Reduz ainda mais a fonte
                        position: 'bottom'
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-regiao"), options);
        chart.render();
        </script>
        """
        return html_code
    else:
        return "Colunas 'Região' ou 'Prec_Ven_Total' não encontradas nos dados."


#Grafico de retabilidade por região
def criar_grafico_por_regiao_pie_rentabilidade(dados_filtrados):
    if 'Região' in dados_filtrados.columns and 'R$_Marg_Contribuicao' in dados_filtrados.columns:
        # Agrupar por 'Região' e calcular o total de rentabilidade
        vendas_regiao = dados_filtrados.groupby('Região')['R$_Marg_Contribuicao'].sum().reset_index()

        # Criar rótulos e valores para o gráfico
        labels = [f"<strong>{regiao} : R$ {valor:,.2f}</strong>" for regiao, valor in zip(vendas_regiao['Região'], vendas_regiao['R$_Marg_Contribuicao'])]
        valores = vendas_regiao['R$_Marg_Contribuicao'].tolist()

        # Gerar o código HTML e JavaScript para o gráfico
        html_code = f"""
        <div id="chart-regiao" style="height: 100%; width: 100%;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'pie',
                height: '100%',  // Ajuste automático de altura
                width: '100%',   // Ajuste automático de largura
            }},
            series: {valores},
            labels: {labels},
            title: {{
                text: 'Rentabilidade por Região',
                align: 'center'
            }},
            legend: {{
                position: 'bottom',
                fontSize: '12px',
                horizontalAlign: 'left'  // Centraliza os itens da legenda
            }},
            tooltip: {{
                y: {{
                    formatter: function(value) {{
                        return 'R$ ' + value.toLocaleString('pt-BR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                    }}
                }}
            }},
            responsive: [{{
                breakpoint: 768,
                options: {{
                    chart: {{
                        height: '400px'  // Para tablets e dispositivos menores
                    }},
                    legend: {{
                        fontSize: '10px'  // Fonte menor em dispositivos menores
                    }}
                }}
            }}, {{
                breakpoint: 480,
                options: {{
                    chart: {{
                        height: '300px'  // Para telas pequenas
                    }},
                    legend: {{
                        fontSize: '9px',  // Reduz ainda mais a fonte
                        position: 'bottom'
                    }}
                }}
            }}]
        }};
        var chart = new ApexCharts(document.querySelector("#chart-regiao"), options);
        chart.render();
        </script>
        """
        return html_code
    else:
        return "Colunas 'Região' ou 'R$_Marg_Contribuicao' não encontradas nos dados."


#grafico de venda região barra
def criar_grafico_por_regiao(dados_filtrados):
    if 'Região' in dados_filtrados.columns and 'Prec_Ven_Total' in dados_filtrados.columns:
        # Agrupar por 'Região' e calcular o total de vendas
        vendas_regiao = dados_filtrados.groupby('Região')['Prec_Ven_Total'].sum().reset_index()

        # Criar rótulos e valores para o gráfico
        labels = vendas_regiao['Região'].tolist()
        valores = vendas_regiao['Prec_Ven_Total'].tolist()

        # Gerar o código HTML e JavaScript para o gráfico de barras
        html_code = f"""
        <div id="chart-regiao" style="height: 100%; width: 100%;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'bar',
                width: '100%',
                height: '400px'
            }},
            series: [{{
                name: 'Vendas',
                data: {valores}
            }}],
            xaxis: {{
                categories: {labels},
                title: {{ text: 'Região' }}
            }},
            yaxis: {{
                labels: {{
                    formatter: function(value) {{
                        return 'R$ ' + value.toLocaleString('pt-BR', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
                    }}
                }},
                title: {{ text: 'Vendas em R$' }}
            }},
            title: {{
                text: 'Vendas por Região',
                align: 'center'
            }},
            legend: {{
                position: 'top',
                fontSize: '10px'
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
        var chart = new ApexCharts(document.querySelector("#chart-regiao"), options);
        chart.render();
        </script>
        """
        return html_code
    else:
        return "Colunas 'Região' ou 'Prec_Ven_Total' não encontradas nos dados."


#Grafico de barra e linha
def criar_grafico_evolucao_vendas_rentabilidade(dados_filtrados):
    if 'Período' in dados_filtrados.columns and 'Prec_Ven_Total' in dados_filtrados.columns and 'R$_Marg_Contribuicao' in dados_filtrados.columns:
        # Convertendo 'Período' para datetime
        dados_filtrados['Período'] = pd.to_datetime(dados_filtrados['Período'], errors='coerce')

        # Agrupando e somando os dados por período
        vendas_por_periodo = dados_filtrados.groupby('Período').agg({
            'Prec_Ven_Total': 'sum',
            'R$_Marg_Contribuicao': 'sum'
        }).reset_index()

        # Calculando a rentabilidade percentual para cada período
        vendas_por_periodo['Rentabilidade (%)'] = (
            vendas_por_periodo['R$_Marg_Contribuicao'] / vendas_por_periodo['Prec_Ven_Total'] * 100
        ).fillna(0)  # Preenchendo com 0 para valores indefinidos

        # Preparando os dados para o gráfico, formatando para exibir apenas o mês
        periodos = vendas_por_periodo['Período'].dt.strftime('%B').tolist()
        vendas = [venda / 1_000_000 for venda in vendas_por_periodo['Prec_Ven_Total']]  # Convertendo para milhões
        rentabilidade = vendas_por_periodo['Rentabilidade (%)'].tolist()

        # Gerar o código HTML e JavaScript para o gráfico
        html_code = f"""
        <div id="chart-evolucao" style="height: 400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        var options = {{
            chart: {{
                type: 'line',
                height: 400,
                stacked: false
            }},
            series: [
                {{
                    name: 'Venda',
                    type: 'column',
                    data: {vendas}
                }},
                {{
                    name: 'Rentabilidade (%)',
                    type: 'line',
                    data: {rentabilidade}
                }}
            ],
            xaxis: {{
                categories: {periodos},
                title: {{ text: '' }}
            }},
            yaxis: [
                {{
                    show: false  // Oculta o eixo y principal (vendas)
                }},
                {{
                    show: false, // Oculta o segundo eixo y (rentabilidade)
                    opposite: true
                }}
            ],
            title: {{
                text: 'Vendas e Rentabilidade',
                align: 'left'
            }},
            legend: {{
                position: 'top'
            }},
            dataLabels: {{
                enabled: true,
                formatter: function(val, opts) {{
                    if (opts.seriesIndex === 1) {{
                        return val.toFixed(2) + '%';
                    }} else {{
                        return '';  // Deixa as vendas sem texto adicional
                    }}
                }}
            }},
            tooltip: {{
                y: {{
                    formatter: function(value, opts) {{
                        if (opts.seriesIndex === 1) {{
                            return value.toFixed(2) + '%';
                        }} else {{
                            return 'R$ ' + value.toFixed(2).toLocaleString('pt-BR') + 'M';
                        }}
                    }}
                }}
            }}
        }};

        var chart = new ApexCharts(document.querySelector("#chart-evolucao"), options);
        chart.render();
        </script>
        """
        
        return html_code
    else:
        return "Colunas 'Período', 'Prec_Ven_Total' ou 'R$_Marg_Contribuicao' não foram encontradas nos dados."

# Grfico com Plotly
def criar_grafico_top_marcas(df, coluna):
    if 'Marca' in df.columns and 'Prec_Ven_Total' in df.columns:
        total_vendas = df['Prec_Ven_Total'].sum()
        top_marcas = df.groupby('Marca').agg({'Prec_Ven_Total': 'sum'}).nlargest(7, 'Prec_Ven_Total').reset_index()
        restante_vendas = total_vendas - top_marcas['Prec_Ven_Total'].sum()
        demais_marcas = pd.DataFrame({'Marca': ['Demais Marcas'], 'Prec_Ven_Total': [restante_vendas]})
        df_final = pd.concat([top_marcas, demais_marcas], ignore_index=True)

        fig = px.bar(df_final, x='Marca', y='Prec_Ven_Total', title="Top 7 Marcas por Vendas", text='Prec_Ven_Total', color='Marca')
        fig.update_layout(yaxis_title="Vendas (R$)", xaxis_title="Marca", showlegend=False)
        fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='inside')
        coluna.plotly_chart(fig, use_container_width=True)
    else:
        coluna.warning("Colunas 'Marca' ou 'Prec_Ven_Total' não encontradas nos dados.")