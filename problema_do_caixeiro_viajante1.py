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
                x_selecionado[i][j
