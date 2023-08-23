# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 20:31:58 2023

@author: Anderson Almeida
"""

import pandas as pd
import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
from folium.plugins import BeautifyIcon

st.set_page_config(page_title="Fuja!", page_icon="🌳")

municipios_sudeste = pd.read_parquet(
    "dados_extraidos_sudeste/municipios_sud.parquet"
)
malhas = gpd.read_parquet(
    "dados_extraidos_sudeste/malhas_sudeste.parquet"
)

st.markdown(f'<h1 style="color:#A3AFBE;font-size:16px;">{"Ajudamos você descobrir novas cidades para o turismo ou em busca de qualidade de vida, longe das grandes cidades"}</h1>', unsafe_allow_html=True)

with st.form("my_form"):
    container1 = st.container()
    col1, col2, col3 = st.columns(3)
    with container1:
        
        with col1:
            municipio_origem = st.selectbox(
                "Sua cidade de origem:", (municipios_sudeste["municipio_x"]), index=1585
            )

            longitude_origem = municipios_sudeste["long"][
                municipios_sudeste["municipio_x"] == municipio_origem
            ].iloc[0]
            latitude_origem = municipios_sudeste["lat"][
                municipios_sudeste["municipio_x"] == municipio_origem
            ].iloc[0]

        with col2:
            raio_km = st.number_input("Raio (Km):", step=10, value=150)
            
        with col3:
            qtd_hab = int(st.number_input(
                "Quantidade Máx. habitantes:", step=5000, value=50_000)
            )
            
            municipios_sudeste = municipios_sudeste[
                municipios_sudeste["PopResid2022"] <= qtd_hab
            ]

            # selecionando as malhas
            malhas = malhas.loc[municipios_sudeste.index.tolist()].reset_index(
                drop=True
            )
            
    # Every form must have a submit button.
    submitted = st.form_submit_button("Fuja!")

    if submitted:
        # Converter o raio para graus usando a abordagem do Haversine
        radius_deg = raio_km / 111.32

        # Criar um ponto representando São Paulo
        ponto_origem = Point(longitude_origem, latitude_origem)

        # Criar um buffer circular em torno do ponto de origem
        buffered_area = ponto_origem.buffer(radius_deg)

        # Realizar a consulta espacial para identificar municípios dentro do buffer
        municipios_dentro_do_raio = malhas[malhas.geometry.within(buffered_area)]

        # mapa
        m = folium.Map(location=[latitude_origem, longitude_origem], zoom_start=7)

        # adicionar cidades dentro do raio
        for index, row in municipios_dentro_do_raio.iterrows():
            
            icon_edit = BeautifyIcon(icon="map-pin",
                                 background_color='transparent',
                                 border_color='transparent',
                                 inner_icon_style='font-size:20px')
            folium.Marker(
                location=[row["geometry"].centroid.y, 
                          row["geometry"].centroid.x],
                popup="{}".format(row["municipio"]),
                icon=icon_edit,
                ).add_to(m)

        # Adicionar um círculo ao mapa
        folium.Circle(
            location=[latitude_origem, longitude_origem],
            radius=raio_km * 1000,  # em metros
            color="brown",
            fill=False,
            dash_array="4, 4",
            fill_color="brown",
            fill_opacity=0.1,
            popup="Circulo com raio de {} km".format(raio_km),
        ).add_to(m)

        # Adicionar um marcador para a cidade de origem
        folium.Marker(
            location=[latitude_origem, longitude_origem],
            popup="{}".format(municipio_origem),
            icon=folium.Icon(icon='home',color="red"),
        ).add_to(m)

        st_data = st_folium(m, use_container_width=True, width=400, height=400)
        
        teste = pd.merge(municipios_sudeste, municipios_dentro_do_raio, on='IBGE7')
        df = pd.DataFrame(teste)
        coluna_para_remover = ['IBGE7', 'geometry', 'municipio_y', 'long', 'lat', 'municipio']
        df = df.drop(coluna_para_remover, axis=1)
        
        renomeando_colunas = {'municipio_x': 'Município', 'UF': 'Estado', 'PopResid2022': 'Habitantes'}
        df = df.rename(columns=renomeando_colunas)
    
        #adicionado uma nova coluna de ordem
        df['Ordem'] = range(1,df['Estado'].size + 1)
        
        #ordem do df
        nova_ordem_colunas = ['Ordem','Município', 'Estado', 'Habitantes']
        df = df[nova_ordem_colunas]

        # Exibir o DataFrame no Streamlit
        # hide_index=True
        st.dataframe(df, use_container_width=True, hide_index=True)