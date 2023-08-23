# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 13:30:30 2023

@author: Anderson Almeida
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

app = Flask(__name__)

municipios_sudeste = pd.read_parquet(
    r"S:\Área de Trabalho\TargetSudeste\dados_extraidos_sudeste\municipios_sud.parquet"
)
malhas = gpd.read_parquet(
    r"S:\Área de Trabalho\TargetSudeste\dados_extraidos_sudeste\malhas_sudeste.parquet"
)

@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "POST":
        municipio_origem = str(request.form.get("municipio_origem"))
        raio_km = float(request.form.get("raio_km"))
        qtd_hab = int(request.form.get("qtd_hab"))
        
        # Converter o raio para graus usando a abordagem do Haversine
        radius_deg = raio_km / 111.32

        # Criar um ponto representando a cidade de origem
        ponto_origem = Point(
            municipios_sudeste["long"].loc[
                municipios_sudeste["municipio_x"] == municipio_origem
            ].iloc[0],
            municipios_sudeste["lat"].loc[
                municipios_sudeste["municipio_x"] == municipio_origem
            ].iloc[0],
        )

        # Criar um buffer circular em torno do ponto de origem
        buffered_area = ponto_origem.buffer(radius_deg)

        # Realizar a consulta espacial para identificar municípios dentro do buffer
        municipios_dentro_do_raio = malhas[malhas.geometry.within(buffered_area)]

        # Criar um mapa Folium
        m = folium.Map(
            location=[
                municipios_sudeste["lat"].loc[
                    municipios_sudeste["municipio_x"] == municipio_origem
                ].iloc[0],
                municipios_sudeste["long"].loc[
                    municipios_sudeste["municipio_x"] == municipio_origem
                ].iloc[0],
            ],
            zoom_start=7
        )

        # Adicionar cidades dentro do raio ao mapa
        for _, row in municipios_dentro_do_raio.iterrows():
            folium.GeoJson(
                row["geometry"],
                style_function=lambda feature: {
                    "weight": 2,
                    "color": "red",
                    "fillColor": "red",
                    "fillOpacity": 0.02,
                },
            ).add_to(m)

        # Adicionar um círculo ao mapa
        folium.Circle(
            location=[
                municipios_sudeste["lat"].loc[
                    municipios_sudeste["municipio_x"] == municipio_origem
                ].iloc[0],
                municipios_sudeste["long"].loc[
                    municipios_sudeste["municipio_x"] == municipio_origem
                ].iloc[0],
            ],
            radius=raio_km * 1000,  # em metros
            color="brown",
            fill=False,
            dash_array="4, 4",
            fill_color="brown",
            fill_opacity=0.1,
            popup="Círculo com raio de {} km".format(raio_km),
        ).add_to(m)

        # Adicionar um marcador para a cidade de origem
        folium.Marker(
            location=[
                municipios_sudeste["lat"].loc[
                    municipios_sudeste["municipio_x"] == municipio_origem
                ].iloc[0],
                municipios_sudeste["long"].loc[
                    municipios_sudeste["municipio_x"] == municipio_origem
                ].iloc[0],
            ],
            popup="{}".format(municipio_origem),
            icon=folium.Icon(color="red"),
        ).add_to(m)

        # Renderizar o mapa no template
        map_html  = m._repr_html_()
        
        return render_template('index.html', map_html=map_html, municipios_sudeste=municipios_sudeste)

    return render_template('index.html', map_html=None, municipios_sudeste=municipios_sudeste)
        

if __name__ == "__main__":
    app.run(debug=True)