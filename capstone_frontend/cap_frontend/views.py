from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import Calls, Trees

import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

def index(request):
    return render(request, 'index.html')
def about(request):
    return render(request, 'about.html')
def analytics(request):
    return render(request, 'analytics.html')

new_orleans_center = {"lon": -90.07, "lat": 29.95}


# Queries data to put on the map
def index(request):

    calls = Calls.objects.exclude(request_status="Closed").values()
    data = pd.DataFrame(list(calls))

    tree_related_311 = data[data['reason'].isin(['Request Tree Service (Right of Way/Public Property)',
       'Tree Stump (removal, grind)',
       'Hurricane Francine Tree-Related Issues or Emergencies',
       'Trucks hitting overhead oak tree limbs',
       'Sidewalk repair after tree removal',
       'Oak tree blocking water line',
       'Tree roots',
       'Christmas Tree Recycle Pick Up'])].copy()

    trees = Trees.objects.values()
    treesdata = pd.DataFrame(list(trees))

    tree_related_311["hover_text"] = (
    "<b>Request Number</b>: " + tree_related_311["request_number"] + 
    "<br><b>Address</b>: " + tree_related_311["address"].astype(str)
    )

    fig = go.Figure()

   fig.add_trace(
        go.Scattermapbox(
            hoverlabel=dict(bgcolor="LightGreen", font_size=12),
            hoverinfo="text",
            hovertext=tree_related_311["hover_text"],
            lat=tree_related_311['latitude'],
            lon=tree_related_311['longitude'],
            mode='markers',
            marker=dict(
                size=20,  # Adjust size if needed
                symbol="tree",  # You can use "marker", "circle", "star", etc.
                allowoverlap=True
            ),
            customdata=tree_related_311[['request_number', 'address', 'reason', 'status', 'date_created']].values.tolist()
        )
    )

    # Set Mapbox layout
    fig.update_layout(
        mapbox=dict(
            map=dict(center=new_orleans_center, zoom=10, style="satellite"),
            #autosize=True,
            width=1200,
            height=900,
            dragmode = 'pan',
            clickmode = 'event+select',
            hovermode='closest'
            style="satellite",  # Or use "streets", "open-street-map"
            accesstoken="pk.eyJ1IjoiZGNpY2VybzIiLCJhIjoiY202c2FkNXN4MDVuOTJrcHc0OWxlaXVjOCJ9.QAnyo9NuHkniCz-_zPqpUA",
            zoom=10,
            
        ),
    )

    plot_html = pio.to_html(fig, full_html=False)

    return render(request, 'index.html', {'plot_html': plot_html})

