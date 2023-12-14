# Caixeiro viajante

# Instalando e importando bibliotecas necessárias

import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pulp
import more_itertools
import openpyxl

from datetime import datetime

# Obtenção dos dados a partir do Excel

df_distancias = pd.read_excel("10_Distancias_em_metros_das_Cidades_do_RN.xlsx", index_col=0)
df_coordenadas = pd.read_excel("10_Cidades_do_RN_-_LAT_LONG.xlsx", index_col=0)

nomes_dos_locais = list(df_distancias.columns.values)

matriz_distancia = df_distancias.to_numpy()

total_de_cidades = len(nomes_dos_locais)

# Modelando Problema

# Definindo o objetivo do modelo

problema_caixeiro = pulp.LpProblem("Problema_Caixeiro", pulp.LpMinimize)

# Definindo as variáveis

x = [[0 for j in range(total_de_cidades)] for i in range(total_de_cidades)]

for local_de_origem in range(total_de_cidades):
    for local_de_destino in range(total_de_cidades):
        if local_de_origem != local_de_destino:
            x[local_de_origem][local_de_destino] = pulp.LpVariable(
                nomes_dos_locais[local_de_origem] + " para " + nomes_dos_locais[local_de_destino], cat='Binary'
            )

# Função objetivo

funcao_objetivo = 0
for local_de_origem in range(total_de_cidades):
    for local_de_destino in range(total_de_cidades):
        if local_de_origem != local_de_destino:
            funcao_objetivo += matriz_distancia[local_de_origem][local_de_destino] * x[local_de_origem][local_de_destino]

# Definir função objetivo

problema_caixeiro += funcao_objetivo

# Restrições

# Restrições de saída

for local_de_origem in range(total_de_cidades):
    restricao_de_saida = 0
    for local_de_destino in range(total_de_cidades):
        if local_de_origem != local_de_destino:
            restricao_de_saida += x[local_de_origem][local_de_destino]

    problema_caixeiro += restricao_de_saida == 1

# Restrições de entrada

for local_de_destino in range(total_de_cidades):
    restricao_de_entrada = 0
    for local_de_origem in range(total_de_cidades):
        if local_de_origem != local_de_destino:
            restricao_de_entrada += x[local_de_origem][local_de_destino]

    problema_caixeiro += restricao_de_entrada == 1

# Restrição de eliminação de sub-rota

conjunto_de_locais = range(total_de_cidades)
for sub_conjunto in list(more_itertools.powerset(conjunto_de_locais)):
    if 2 <= len(sub_conjunto) <= len(conjunto_de_locais) - 1:
        restricao_subrota = 0
        for local_de_origem in sub_conjunto:
            for local_de_destino in sub_conjunto:
                restricao_subrota += x[local_de_origem][local_de_destino]
        problema_caixeiro += restricao_subrota <= len(sub_conjunto) - 1

# Resolvendo modelo

# Checando status da solução

tempo_inicial = datetime.now()

status = problema_caixeiro.solve()

tempo_final = datetime.now()

print(tempo_final - tempo_inicial)

pulp.LpStatus[status]

# Verificando valores das variáveis

for variavel in problema_caixeiro.variables():
    if variavel.varValue > 0:
        print(variavel.name, "=", variavel.varValue)

print(pulp.value(problema_caixeiro.objective))

# Interface Streamlit
st.title("Dashboard do Problema do Caixeiro Viajante")

# Exibir as cidades disponíveis
st.write("Cidades Disponíveis:")
cidades_selecionadas = st.multiselect("Selecione as cidades:", nomes_dos_locais)
st.write(cidades_selecionadas)

# Selecione o número de cidades para visitar
num_cidades_a_visitar = st.slider("Selecione o número de cidades para visitar:", 2, total_de_cidades, 5)

# Botão para resolver o problema
if st.button("Resolver Problema"):
    # Resolver o modelo apenas para as cidades selecionadas
    df_distancias_selecionadas = df_distancias.loc[cidades_selecionadas, cidades_selecionadas]

    # Criar o modelo apenas para as cidades selecionadas
    total_de_cidades_selecionadas = len(cidades_selecionadas)
    problema_caixeiro_selecionado = pulp.LpProblem("Problema_Caixeiro", pulp.LpMinimize)

    # Definir variáveis para as cidades selecionadas
    x_selecionado = [[0 for j in range(total_de_cidades_selecionadas)] for i in range(total_de_cidades_selecionadas)]
    for i, local_de_origem in enumerate(cidades_selecionadas):
        for j, local_de_destino in enumerate(cidades_selecionadas):
            if i != j:
                x_selecionado[i][j                ] = pulp.LpVariable(
                    local_de_origem + " para " + local_de_destino, cat='Binary'
                )

    # Função objetivo para as cidades selecionadas
    funcao_objetivo_selecionado = 0
    for i, local_de_origem in enumerate(cidades_selecionadas):
        for j, local_de_destino in enumerate(cidades_selecionadas):
            if i != j:
                funcao_objetivo_selecionado += (
                    df_distancias_selecionadas.iloc[i, j] * x_selecionado[i][j]
                )

    # Definir função objetivo para as cidades selecionadas
    problema_caixeiro_selecionado += funcao_objetivo_selecionado

    # Restrições de saída para as cidades selecionadas
    for i, local_de_origem in enumerate(cidades_selecionadas):
        restricao_de_saida_selecionado = 0
        for j, local_de_destino in enumerate(cidades_selecionadas):
            if i != j:
                restricao_de_saida_selecionado += x_selecionado[i][j]

        problema_caixeiro_selecionado += restricao_de_saida_selecionado == 1

    # Restrições de entrada para as cidades selecionadas
    for j, local_de_destino in enumerate(cidades_selecionadas):
        restricao_de_entrada_selecionado = 0
        for i, local_de_origem in enumerate(cidades_selecionadas):
            if i != j:
                restricao_de_entrada_selecionado += x_selecionado[i][j]

        problema_caixeiro_selecionado += restricao_de_entrada_selecionado == 1

    # Restrição de eliminação de sub-rota para as cidades selecionadas
    conjunto_de_locais_selecionados = range(total_de_cidades_selecionadas)
    for sub_conjunto_selecionado in list(
        more_itertools.powerset(conjunto_de_locais_selecionados)
    ):
        if 2 <= len(sub_conjunto_selecionado) <= total_de_cidades_selecionadas - 1:
            restricao_subrota_selecionado = 0
            for i, local_de_origem in enumerate(cidades_selecionadas):
                if i in sub_conjunto_selecionado:
                    for j, local_de_destino in enumerate(cidades_selecionadas):
                        if j in sub_conjunto_selecionado:
                            restricao_subrota_selecionado += x_selecionado[i][j]

            problema_caixeiro_selecionado += (
                restricao_subrota_selecionado <= len(sub_conjunto_selecionado) - 1
            )

    # Resolver modelo para as cidades selecionadas
    tempo_inicial_selecionado = datetime.now()
    status_selecionado = problema_caixeiro_selecionado.solve()
    tempo_final_selecionado = datetime.now()

    # Exibir status da solução
    st.write("Status da Solução para as cidades selecionadas:", pulp.LpStatus[status_selecionado])
    st.write("Tempo de Resolução para as cidades selecionadas:", tempo_final_selecionado - tempo_inicial_selecionado)

    # Exibir o caminho percorrido para as cidades selecionadas
    caminho_percorrido_selecionado = []
    for i, local_de_origem in enumerate(cidades_selecionadas):
        for j, local_de_destino in enumerate(cidades_selecionadas):
            if i != j and pulp.value(x_selecionado[i][j]) > 0:
                caminho_percorrido_selecionado.append((local_de_origem, local_de_destino))

    st.write("Caminho Percorrido para as cidades selecionadas:")
    st.write(caminho_percorrido_selecionado)

    # Plotar o mapa com o caminho para as cidades selecionadas
    # Adapte esta parte com a biblioteca que preferir para plotar mapas
    # Você pode usar folium, matplotlib basemap toolkit, ou outras opções

    # Exemplo com folium

    # Carregue os dados geográficos do Rio Grande do Norte usando geobr
    brasil = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    rn = brasil.cx[-40:-30, -65:-35]  # Ajuste as coordenadas conforme necessário

    # Crie um GeoDataFrame para as cidades do RN
    gdf_cidades = gpd.GeoDataFrame(
        df_coordenadas,
        geometry=gpd.points_from_xy(df_coordenadas["Longitude"], df_coordenadas["Latitude"]),
        crs="EPSG:4326"  # Coordenadas lat/lon
    )

    # Crie um GeoDataFrame para o caminho percorrido
    caminho_df_selecionado = pd.DataFrame(caminho_percorrido_selecionado, columns=["Origem", "Destino"])
    gdf_caminho_selecionado = gdf_cidades.merge(
        caminho_df_selecionado, how="inner", left_on="Cidade", right_on="Origem"
    )

    # Plotagem do mapa
    fig_selecionado, ax_selecionado = plt.subplots(figsize=(10, 10))
    rn.boundary.plot(ax=ax_selecionado, linewidth=2, aspect=1)  # Ajuste o GeoDataFrame para o RN em vez de usar o mundo
    gdf_cidades.plot(ax=ax_selecionado, color="blue", marker="o", markersize=50, label="Cidades")
    gdf_caminho_selecionado.plot(
        ax=ax_selecionado, color="red", linewidth=3, linestyle="-", label="Caminho Percorrido"
    )

    # Adicione rótulos para as cidades
    for i, txt in enumerate(df_coordenadas.columns):
        ax_selecionado.annotate(
            txt, (df_coordenadas.iloc[i]["Longitude"], df_coordenadas.iloc[i]["Latitude"]), fontsize=8
        )

    # Adicione rótulos para o caminho percorrido
    for aresta in caminho_percorrido_selecionado:
        origem, destino = aresta
        origem_coord = (
            df_coordenadas.loc[origem]["Longitude"], df_coordenadas.loc[origem]["Latitude"]
        )
        destino_coord = (
            df_coordenadas.loc[destino]["Longitude"], df_coordenadas.loc[destino]["Latitude"]
        )
        ax_selecionado.annotate(
            "", xy=destino_coord, xytext=origem_coord, arrowprops=dict(arrowstyle="->", linewidth=1, color="black")
        )

    ax_selecionado.set_title("Mapa do RN com Caminho Percorrido para as cidades selecionadas")
    ax_selecionado.legend()

    # Exiba o mapa no Streamlit
    st.pyplot(fig_selecionado)

