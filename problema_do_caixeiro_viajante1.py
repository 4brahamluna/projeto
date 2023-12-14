# Caixeiro viajante

# Instalando e importando bibliotecas necessárias
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pulp
import more_itertools
from datetime import datetime
import openpyxl

# Obtenção dos dados a partir do Excel
df_distancias = pd.read_excel("10_Distancias_em_metros_das_Cidades_do_RN.xlsx", index_col=0)
df_coordenadas = pd.read_excel("10_Cidades_do_RN_-_LAT_LONG.xlsx", index_col=0)

nomes_dos_locais = list(df_distancias.columns.values)
matriz_distancia = df_distancias.to_numpy()
total_de_cidades = len(nomes_dos_locais)

# Modelando Problema
problema_caixeiro = pulp.LpProblem("Problema_Caixeiro", pulp.LpMinimize)

# Definindo as variáveis
x = [[0 for j in range(total_de_cidades)] for i in range(total_de_cidades)]
for local_de_origem in range(total_de_cidades):
    for local_de_destino in range(total_de_cidades):
        if local_de_origem != local_de_destino:
            x[local_de_origem][local_de_destino] = pulp.LpVariable(
                f"{nomes_dos_locais[local_de_origem]} para {nomes_dos_locais[local_de_destino]}", cat='Binary'
            )

# Função objetivo
funcao_objetivo = 0
for local_de_origem in range(total_de_cidades):
    for local_de_destino in range(total_de_cidades):
        if local_de_origem != local_de_destino:
            funcao_objetivo += matriz_distancia[local_de_origem][local_de_destino] * x[local_de_origem][local_de_destino]

# Definir função objetivo
problema_caixeiro += funcao_objetivo

# Restrições...

# Interface Streamlit
st.title("Dashboard do Problema do Caixeiro Viajante")

# Exibir as cidades disponíveis
st.write("Cidades Disponíveis:")
st.write(nomes_dos_locais)

# Selecione o número de cidades para visitar
num_cidades_a_visitar = st.slider("Selecione o número de cidades para visitar:", 2, total_de_cidades, 5)

# Botão para resolver o problema
if st.button("Resolver Problema"):
    # Resolver o modelo
    tempo_inicial = datetime.now()
    status = problema_caixeiro.solve()
    tempo_final = datetime.now()

    # Exibir status da solução
    st.write("Status da Solução:", pulp.LpStatus[status])
    st.write("Tempo de Resolução:", tempo_final - tempo_inicial)

    # Exibir o caminho percorrido
    caminho_percorrido = []
    for var in problema_caixeiro.variables():
        if var.varValue > 0:
            origem, destino = var.name.split("para")
            origem = origem.strip()  # Remova espaços em branco adicionais
            destino = destino.strip()  # Remova espaços em branco adicionais
            caminho_percorrido.append((origem, destino))

    st.write("Caminho Percorrido:")
    st.write(caminho_percorrido)

    # Plotar o mapa com o caminho
    # Adapte esta parte com a biblioteca que preferir para plotar mapas
    # Você pode usar geopandas, matplotlib, folium ou outras opções

    # Exemplo com geopandas e matplotlib
    gdf_cidades = gpd.GeoDataFrame(
        df_coordenadas,
        geometry=gpd.points_from_xy(df_coordenadas["Longitude"], df_coordenadas["Latitude"]),
        crs="EPSG:4326"  # Coordenadas lat/lon
    )

    # Extrair origens e destinos do caminho percorrido
    origens, destinos = zip(*caminho_percorrido)

    # Criar um GeoDataFrame apenas com os locais do caminho percorrido
    gdf_caminho = gdf_cidades[gdf_cidades.index.isin(origens + destinos)]

    # Plotagem do mapa
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_cidades.boundary.plot(ax=ax, linewidth=2, aspect=1)
    gdf_cidades.plot(ax=ax, color="blue", marker="o", markersize=50, label="Cidades")
    gdf_caminho.plot(ax=ax, color="red", linewidth=3, linestyle="-", label="Caminho Percorrido")

    for i, txt in enumerate(df_coordenadas.columns):
        ax.annotate(txt, (df_coordenadas.iloc[i]["Longitude"], df_coordenadas.iloc[i]["Latitude"]), fontsize=8)

    for aresta in caminho_percorrido:
        origem, destino = aresta
        origem_coord = (df_coordenadas.loc[origem]["Longitude"], df_coordenadas.loc[origem]["Latitude"])
        destino_coord = (df_coordenadas.loc[destino]["Longitude"], df_coordenadas.loc[destino]["Latitude"])
        ax.annotate("", xy=destino_coord, xytext=origem_coord, arrowprops=dict(arrowstyle="->", linewidth=1, color="black"))

    ax.set_title("Mapa do RN com Caminho Percorrido")
    ax.legend()

    # Exiba o mapa no Streamlit
    st.pyplot(fig)
