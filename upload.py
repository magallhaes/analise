import streamlit as st
import os
import pandas as pd

# Definir o caminho da pasta onde os arquivos serão salvos
save_folder = "db"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Upload do arquivo
uploaded_file = st.sidebar.file_uploader("Upload da planilha análise.xlsm", type=["xlsx", "xlsm"])

if uploaded_file is not None:
    # Salvar o arquivo na pasta 'db'
    save_path = os.path.join(save_folder, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Arquivo salvo com sucesso em: {save_path}")

    # Carregar a aba "DADOS" e exibir as primeiras linhas
    df = pd.read_excel(save_path, sheet_name="DADOS")
    st.write("Visualizando as primeiras linhas da aba 'DADOS':")
    st.dataframe(df.head())