#Caixeiro viajante

#Instalando e importando bibliotecas necessárias
pip install -r requirements.txt

import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


from datetime import datetime

# Obtenção dos dados a partir do Excel

df_distancias = pd.read_excel("10_Distancias_em_metros_das_Cidades_do_RN.xlsx", index_col=0)
df_coordenadas = pd.read_excel("10_Cidades_do_RN_-_LAT_LONG.xlsx", index_col=0)
#print(df_distancias)

nomes_dos_locais = list(df_distancias.columns.values)

nomes_dos_locais

matriz_distancia = df_distancias.to_numpy()

total_de_cidades = len(nomes_dos_locais)

#Modelando Problema

#Definindo o objetivo do modelo

problema_caixeiro = pulp.LpProblem("Problema_Caixeiro",pulp.LpMinimize)

#Aqui definimos que o modelo é de minimização

#Definindo as variáveis

x = [[0 for j in range(total_de_cidades)] for i in range(total_de_cidades)]

for local_de_origem in range(total_de_cidades):
  for local_de_destino in range(total_de_cidades):
    if local_de_origem != local_de_destino:
      x[local_de_origem][local_de_destino] = pulp.LpVariable(nomes_dos_locais[local_de_origem] + " para " + nomes_dos_locais[local_de_destino], cat='Binary')

#Função objetivo

funcao_objetivo = 0
for local_de_origem in range(total_de_cidades):
  for local_de_destino in range(total_de_cidades):
    if local_de_origem != local_de_destino:
      funcao_objetivo += matriz_distancia[local_de_origem][local_de_destino] * x[local_de_origem][local_de_destino]
#funcao_objetivo

#Definir função objetivo

problema_caixeiro += funcao_objetivo

#Restrições

#Restrições de saída

for local_de_origem in range(total_de_cidades):
  restricao_de_saida = 0
  for local_de_destino in range(total_de_cidades):
    if local_de_origem != local_de_destino:
      restricao_de_saida += x[local_de_origem][local_de_destino]

  problema_caixeiro += restricao_de_saida == 1

#Restrições de entrada

for local_de_destino in range(total_de_cidades):
  restricao_de_entrada = 0
  for local_de_origem in range(total_de_cidades):
    if local_de_origem != local_de_destino:
      restricao_de_entrada += x[local_de_origem][local_de_destino]

  problema_caixeiro += restricao_de_entrada == 1

#Restrição de eliminação de sub-rota

conjunto_de_locais = range(total_de_cidades)
for sub_conjunto in list(more_itertools.powerset(conjunto_de_locais)):
  if len(sub_conjunto) >= 2 and len(sub_conjunto) <= len(conjunto_de_locais) - 1:
    #print(sub_conjunto)
    restricao_subrota = 0
    for local_de_origem in sub_conjunto:
      for local_de_destino in sub_conjunto:
        restricao_subrota += x[local_de_origem][local_de_destino]
    problema_caixeiro += restricao_subrota <= len(sub_conjunto) - 1

#Resolvendo modelo

#Checando status da solução

tempo_inicial = datetime.now()

status = problema_caixeiro.solve()

tempo_final = datetime.now()

print(tempo_final - tempo_inicial)

pulp.LpStatus[status]

#Verificando valores das variáveis

for variavel in problema_caixeiro.variables():
  if variavel.varValue > 0:
    print(variavel.name, "=", variavel.varValue)

print(pulp.value(problema_caixeiro.objective))



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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
            origem, destino = var.name.split("_para_")
            caminho_percorrido.append((origem, destino))

    st.write("Caminho Percorrido:")
    st.write(caminho_percorrido)

    # Plotar o mapa com o caminho
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
    caminho_df = pd.DataFrame(caminho_percorrido, columns=["Origem", "Destino"])
    gdf_caminho = gdf_cidades.merge(caminho_df, how="inner", left_on="Cidade", right_on="Origem")
    
    # Plotagem do mapa
    fig, ax = plt.subplots(figsize=(10, 10))
    rn.boundary.plot(ax=ax, linewidth=2, aspect=1)  # Ajuste o GeoDataFrame para o RN em vez de usar o mundo
    gdf_cidades.plot(ax=ax, color="blue", marker="o", markersize=50, label="Cidades")
    gdf_caminho.plot(ax=ax, color="red", linewidth=3, linestyle="-", label="Caminho Percorrido")
    
    # Adicione rótulos para as cidades
    for i, txt in enumerate(df_coordenadas.columns):
        ax.annotate(txt, (df_coordenadas.iloc[i]["Longitude"], df_coordenadas.iloc[i]["Latitude"]), fontsize=8)
    
    # Adicione rótulos para o caminho percorrido
    for aresta in caminho_percorrido:
        origem, destino = aresta
        origem_coord = (df_coordenadas.loc[origem]["Longitude"], df_coordenadas.loc[origem]["Latitude"])
        destino_coord = (df_coordenadas.loc[destino]["Longitude"], df_coordenadas.loc[destino]["Latitude"])
        ax.annotate("", xy=destino_coord, xytext=origem_coord, arrowprops=dict(arrowstyle="->", linewidth=1, color="black"))
    
    ax.set_title("Mapa do RN com Caminho Percorrido")
    ax.legend()
    
    # Exiba o mapa no Streamlit
    st.pyplot(fig)
