from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

def home(request):
    return render(request, 'index.html')
    #template = loader.get_template('home.html')
    #return HttpResponse(template.render({}, request))


df_311_open = pd.DataFrame({
    'Latitude': [29.95, 29.96, 29.97],
    'Longitude': [-90.07, -90.06, -90.05],
    'TREE_ID': [1, 2, 3]
})

new_orleans_center = {"lon": -90.07, "lat": 29.95}


# Add dummy data to the map of NOLA
def index(request):
    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=df_311_open['Latitude'],
            lon=df_311_open['Longitude'],
            text=df_311_open['TREE_ID'],
            mode='markers',
            marker=dict(size=6, color='red'),
            name='Open Tree-Related 311 Reports'
        )
    )

    fig.update_layout(
        mapbox=dict(center=new_orleans_center, zoom=10, style="open-street-map")
    )

    plot_html = pio.to_html(fig, full_html=False)

    return render(request, 'index.html', {'plot_html': plot_html})