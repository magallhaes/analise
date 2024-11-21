import streamlit as st
import pandas as pd
from typing import Optional
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
#import locale
from typing import Optional

def criar_grafico_evolucao_vendas(dados: pd.DataFrame) -> Optional[go.Figure]:
    """
    Cria um gráfico de linha mostrando a evolução das vendas ao longo do tempo.
    
    Args:
        dados (pd.DataFrame): DataFrame com colunas 'Período' e 'Prec_Ven_Total'
    
    Returns:
        Optional[go.Figure]: Objeto do gráfico ou None se as colunas necessárias não existirem
    """
    if 'Período' in dados.columns and 'Prec_Ven_Total' in dados.columns:
        dados_agrupados = dados.groupby('Período')['Prec_Ven_Total'].sum().reset_index()
        fig = px.line(dados_agrupados, 
                     x='Período', 
                     y='Prec_Ven_Total',
                     title='Evolução das Vendas',
                     labels={'Período': 'Data',
                            'Prec_Ven_Total': 'Total de Vendas (R$)'})
        
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Total de Vendas (R$)",
            hovermode='x unified'
        )
        
        # Formatação dos valores em reais
        fig.update_traces(
            hovertemplate='Data: %{x}<br>Vendas: R$ %{y:,.2f}<extra></extra>'
        )
        
        return fig
    return None

def criar_grafico_top_marcas(df: pd.DataFrame, coluna: str) -> Optional[go.Figure]:
    """
    Cria um gráfico de pizza 3D com as top 7 marcas por vendas.
    
    Args:
        df (pd.DataFrame): DataFrame com colunas 'Marca' e 'Prec_Ven_Total'
        coluna (str): Nome da coluna Streamlit para exibição
    
    Returns:
        Optional[go.Figure]: Objeto do gráfico ou None se as colunas necessárias não existirem
    """
    if 'Marca' in df.columns and 'Prec_Ven_Total' in df.columns:
        # Agrupar por marca e obter o total de vendas
        total_vendas = df['Prec_Ven_Total'].sum()
        top_marcas = (df.groupby('Marca')
                     .agg({'Prec_Ven_Total': 'sum'})
                     .nlargest(7, 'Prec_Ven_Total')
                     .reset_index())
        
        # Calcular e adicionar "Demais Marcas"
        restante_vendas = total_vendas - top_marcas['Prec_Ven_Total'].sum()
        demais_marcas = pd.DataFrame({
            'Marca': ['Demais Marcas'],
            'Prec_Ven_Total': [restante_vendas]
        })
        
        df_final = pd.concat([top_marcas, demais_marcas], ignore_index=True)
        
        # Criar gráfico de pizza 3D
        fig = go.Figure(data=[go.Pie(
            labels=df_final['Marca'],
            values=df_final['Prec_Ven_Total'],
            hole=0.4,
            pull=0.05,
            textinfo='label+percent',
            textposition='inside',
            marker=dict(line=dict(color='#FFFFFF', width=1))
        )])
        
        fig.update_layout(
            title="Top 7 Marcas por Vendas",
            annotations=[dict(text='', x=0.5, y=0.5, font_size=20, showarrow=False)],
            showlegend=False
        )
        
        return fig
    return None

def criar_grafico_top_grupos(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Cria um gráfico de rosca com os top 7 grupos por vendas, exibindo os rótulos diretamente no gráfico.
    
    Args:
        df (pd.DataFrame): DataFrame com colunas 'Grupo' e 'Prec_Ven_Total'.
    
    Returns:
        Optional[go.Figure]: Objeto do gráfico ou None se as colunas necessárias não existirem.
    """
    if 'Grupo' in df.columns and 'Prec_Ven_Total' in df.columns:
        # Agrupar por grupo e obter o total de vendas
        total_vendas = df['Prec_Ven_Total'].sum()
        top_grupos = (df.groupby('Grupo')
                     .agg({'Prec_Ven_Total': 'sum'})
                     .nlargest(7, 'Prec_Ven_Total')
                     .reset_index())
        
        # Calcular e adicionar "Demais Grupos"
        restante_vendas = total_vendas - top_grupos['Prec_Ven_Total'].sum()
        demais_grupos = pd.DataFrame({
            'Grupo': ['Demais Grupos'],
            'Prec_Ven_Total': [restante_vendas]
        })
        
        df_final = pd.concat([top_grupos, demais_grupos], ignore_index=True)
        
        # Criar gráfico de rosca
        fig = px.pie(df_final, 
                     names='Grupo', 
                     values='Prec_Ven_Total', 
                     title="Top 7 Grupos por Vendas",
                     hole=0.4,  # Define o tamanho do "furo" no centro para criar o efeito de rosca
                     color_discrete_sequence=px.colors.qualitative.Set3)
        
        # Ajustes para exibir rótulos diretamente no gráfico
        fig.update_traces(
            textinfo='percent+label',
            textposition='inside',
            hovertemplate='Grupo: %{label}<br>Vendas: R$ %{value:,.2f}<extra></extra>'
        )
        
        fig.update_layout(
            showlegend=False,  # Remove a legenda lateral
            hoverlabel=dict(bgcolor="white")
        )
        
        return fig
    return None





def criar_grafico_distribuicao_grupo(dados_filtrados: pd.DataFrame, coluna: str) -> Optional[go.Figure]:
    """
    Cria um gráfico de barras mostrando a distribuição de vendas por grupo.
    
    Args:
        dados_filtrados (pd.DataFrame): DataFrame com os dados filtrados
        coluna (str): Nome da coluna para agrupamento
    
    Returns:
        Optional[go.Figure]: Objeto do gráfico ou None se as colunas necessárias não existirem
    """
    if coluna in dados_filtrados.columns and 'Prec_Ven_Total' in dados_filtrados.columns:
        dados_agrupados = (dados_filtrados.groupby(coluna)['Prec_Ven_Total']
                          .sum()
                          .reset_index()
                          .sort_values('Prec_Ven_Total', ascending=False))
        
        fig = px.bar(dados_agrupados,
                    x=coluna,
                    y='Prec_Ven_Total',
                    title=f"Distribuição de Vendas por {coluna}",
                    color=coluna,
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    text='Prec_Ven_Total')
        
        fig.update_layout(
            xaxis_title=coluna,
            yaxis_title="Total de Vendas (R$)",
            showlegend=False,
            hoverlabel=dict(bgcolor="white"),
            hovermode='x unified'
        )
        
        # Formatação dos valores em reais
        fig.update_traces(
            texttemplate='R$ %{text:,.2f}',
            textposition='inside',
            hovertemplate=f'{coluna}: %{{x}}<br>Vendas: R$ %{{y:,.2f}}<extra></extra>'
        )
        
        return fig
    return None

def criar_grafico_vendas_por_vendedor(dados: pd.DataFrame) -> Optional[go.Figure]:
    """
    Cria um gráfico de barras mostrando as vendas por vendedor.
    
    Args:
        dados (pd.DataFrame): DataFrame com colunas 'Vendedor' e 'Prec_Ven_Total'
    
    Returns:
        Optional[go.Figure]: Objeto do gráfico ou None se as colunas necessárias não existirem
    """
    if 'Vendedor' in dados.columns and 'Prec_Ven_Total' in dados.columns:
        dados_agrupados = (dados.groupby('Vendedor')['Prec_Ven_Total']
                          .sum()
                          .reset_index()
                          .sort_values('Prec_Ven_Total', ascending=False))
        
        fig = px.bar(dados_agrupados,
                    x='Vendedor',
                    y='Prec_Ven_Total',
                    title='Vendas por Vendedor',
                    color='Vendedor',
                    text='Prec_Ven_Total')
        
        fig.update_layout(
            xaxis_title="Vendedor",
            yaxis_title="Total de Vendas (R$)",
            showlegend=False,
            hoverlabel=dict(bgcolor="white")
        )
        
        fig.update_traces(
            texttemplate='R$ %{text:,.2f}',
            textposition='inside',
            hovertemplate='Vendedor: %{x}<br>Vendas: R$ %{y:,.2f}<extra></extra>'
        )
        
        return fig
    return None


def criar_grafico_vendas_menos_incentivo(dados: pd.DataFrame) -> Optional[go.Figure]:
    """
    Cria um gráfico mostrando os produtos com mais vendas e menor incentivo.
    
    Args:
        dados (pd.DataFrame): DataFrame com colunas 'Produto', 'Prec_Ven_Total' e 'Incentivo'
    
    Returns:
        Optional[go.Figure]: Objeto do gráfico ou None se as colunas necessárias não existirem
    """
    # Verifica se as colunas necessárias estão no DataFrame
    if 'Produto' in dados.columns and 'Prec_Ven_Total' in dados.columns and 'R$_Inc_Venda' in dados.columns:
        # Agrupa os dados por produto, somando o total de vendas e incentivo por produto
        dados_agrupados = (dados.groupby('Produto')
                           .agg({'Prec_Ven_Total': 'sum', 'R$_Inc_Venda': 'sum'})
                           .reset_index())
        
        # Ordena os produtos por vendas em ordem decrescente e depois por incentivo em ordem crescente
        dados_agrupados = dados_agrupados.sort_values(by=['Prec_Ven_Total', 'R$_Inc_Venda'], 
                                                      ascending=[False, True])
        
        # Seleciona os top 10 produtos com mais vendas e menor incentivo
        top_produtos = dados_agrupados.head(10)
        
        # Cria um gráfico de barras para visualizar as vendas e incentivos
        fig = go.Figure()
        
        # Adiciona uma barra para as vendas
        fig.add_trace(go.Bar(
            x=top_produtos['Produto'],
            y=top_produtos['Prec_Ven_Total'],
            name='Vendas (R$)',
            marker_color='lightskyblue'
        ))
        
        # Adiciona uma barra para os incentivos
        fig.add_trace(go.Bar(
            x=top_produtos['Produto'],
            y=top_produtos['R$_Inc_Venda'],
            name='Incentivo (R$)',
            marker_color='lightcoral'
        ))
        
        # Configurações adicionais do gráfico
        fig.update_layout(
            title="Top 10 Produtos com Maior Vendas e Menor Incentivo",
            xaxis_title="Produto",
            yaxis_title="Valores (R$)",
            barmode='group',
            hovermode='x unified'
        )
        
        fig.update_traces(
            hovertemplate='Produto: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>'
        )
        
        return fig
    return None
