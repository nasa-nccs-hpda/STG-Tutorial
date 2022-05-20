import branca.colormap as cm
import folium
from folium import Map, TileLayer, GeoJson, LayerControl, Icon, Marker, features, Figure, CircleMarker, plugins
from matplotlib.colors import LinearSegmentedColormap
import geopandas as gpd
import pandas as pd
import rioxarray as rxr
import numpy as np

basemaps = {
       'Google Terrain' : TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Terrain',
        overlay = False,
        control = True
       ),
        'basemap_gray' : TileLayer(
            tiles="http://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
            opacity=1,
            name="World gray basemap",
            attr="ESRI",
            overlay=False
        ),
        'Imagery' : TileLayer(
            tiles='https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            opacity=1,
            name="World Imagery",
            attr="ESRI",
            overlay=False
        ),
        'ESRINatGeo' : TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
            opacity=1,
            name='ESRI NatGeo',
            attr='ESRI',
            overlay=False
        )
}

def ADD_ATL08_OBS_TO_MAP(atl08_gdf, MAP_COL, DO_NIGHT, NIGHT_FLAG_NAME, foliumMap, RADIUS=10):
    
    pal_height_cmap = cm.LinearColormap(
        colors = ['black','#636363','#fc8d59','#fee08b','#ffffbf','#d9ef8b','#91cf60','#1a9850'], 
        vmin=0, 
        vmax=25)

    pal_height_cmap.caption = f'Vegetation height from  ATL08 ({MAP_COL})'
    
    night_flg_label = 'day/night'
    if DO_NIGHT:
        atl08_gdf = atl08_gdf[atl08_gdf[NIGHT_FLAG_NAME]== 1]
        night_flg_label = 'night'
    print(f'Mapping {len(atl08_gdf)} {night_flg_label} ATL08 observations of {MAP_COL}')
    
    # https://stackoverflow.com/questions/61263787/folium-featuregroup-in-python
    #feature_group = folium.FeatureGroup('ATL08')
    
    atl08_cols_zip_list = [atl08_gdf.lat, atl08_gdf.lon, atl08_gdf[MAP_COL]]
        
    for lat, lon, ht in zip(*atl08_cols_zip_list):
        ATL08_obs_night = CircleMarker(location=[lat, lon],
                                radius = RADIUS,
                                weight = 0.75,
                                tooltip = str(round(ht,2))+" m",
                                fill=True,
                                #fill_color=getfill(h_can),
                                color = pal_height_cmap(ht),
                                opacity = 1,
                                name = f"ATL08 {night_flg_label} obs"
                   )
        ATL08_obs_night.add_to(foliumMap)
    foliumMap.add_child(pal_height_cmap)
    return foliumMap



def MAP_ATL08_FOLIUM(atl08_gdf, MAP_COL='h_can', DO_NIGHT=True, NIGHT_FLAG_NAME='night_flg' , \
    ADD_LAYER=True, LAYER_FN=None, basemaps=basemaps, fig_w=1000, fig_h=400, RADIUS=10):
    
    if LAYER_FN is None:
        ADD_LAYER=False
    
    # Get a basemap
    #tiler_basemap_gray = "http://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
    #tiler_basemap_image = 'https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

    #Map the Layers
    Map_Figure=Figure(width=fig_w,height=fig_h)
    
    #------------------
    foliumMap = Map(
        #tiles="Stamen Toner",
        #tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        #attr = 'ESRI World Imagery',
        #name = 'ESRI World Imagery',
        location=(atl08_gdf.lat.mean(), atl08_gdf.lon.mean()),
        zoom_start=8, control_scale=True, tiles=None
    )
    Map_Figure.add_child(foliumMap)
    
    basemaps['Imagery'].add_to(foliumMap)
    basemaps['basemap_gray'].add_to(foliumMap)
    basemaps['ESRINatGeo'].add_to(foliumMap)
     
    if ADD_LAYER:
        lyr = gpd.read_file(LAYER_FN)
        lyrs = gpd.GeoDataFrame( pd.concat( [lyr], ignore_index=True) )
        lyr_style = {'fillColor': 'gray', 'color': 'gray', 'weight' : 0.75, 'opacity': 1, 'fillOpacity': 0.5}
        GeoJson(lyrs, name="HRSI CHM footprints", style_function=lambda x:lyr_style).add_to(foliumMap)

    foliumMap = ADD_ATL08_OBS_TO_MAP(atl08_gdf, MAP_COL=MAP_COL, DO_NIGHT=DO_NIGHT, NIGHT_FLAG_NAME=NIGHT_FLAG_NAME, foliumMap=foliumMap, RADIUS=RADIUS)
    #foliumMap.add_child(LayerControl()) #LayerControl().add_to(foliumMap)
    
    LayerControl().add_to(foliumMap)
    ## Add fullscreen button
    plugins.Fullscreen().add_to(foliumMap)
    ##plugins.Geocoder().add_to(foliumMap)
    plugins.MousePosition().add_to(foliumMap)
    minimap = plugins.MiniMap()
    foliumMap.add_child(minimap)
    
    return foliumMap


