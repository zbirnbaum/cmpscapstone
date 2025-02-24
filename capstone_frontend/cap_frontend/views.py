
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import render
from .models import Calls, Trees
from math import sqrt

import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
import numpy as np

def index(request):
    return render(request, 'index.html')
def about(request):
    return render(request, 'about.html')
def analytics(request):
    return render(request, 'analytics.html')


def get_nearest_trees_from_db(lat, lon):
    lat, lon = float(lat), float(lon)

    # Fetch all trees from the database and convert to dataframe with separate lat and long columns
    trees = Trees.objects.values('tree_id', 'location')
    treesdata = pd.DataFrame(list(trees))
    treesdata[['latitude', 'longitude']] = treesdata['location'].str.extract(r'\(([^,]+), ([^)]+)\)').astype(float)
    
    # Compute Euclidean distance
    treesdata['distance'] = ((treesdata['latitude'] - lat) ** 2 + (treesdata['longitude'] - lon) ** 2).apply(sqrt)

    # Sort by distance and return the k nearest trees
    nearest_trees = treesdata.nsmallest(3, 'distance')[['tree_id', 'latitude', 'longitude']].to_dict(orient='records')
    return nearest_trees

def nears(request):
    lat = float(request.GET.get('lat'))
    lon = float(request.GET.get('lon'))

    nearest_trees = get_nearest_trees_from_db(lat, lon) 

    response = JsonResponse({"nearest_trees": nearest_trees}, safe=False)
    return response


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
        go.Scattermap(
            hoverlabel=dict(bgcolor="#90EE90", font_size=12),
            hoverinfo="text",
            hovertext = tree_related_311["hover_text"],
            lat=tree_related_311['latitude'],
            lon=tree_related_311['longitude'],
            mode='markers',
            marker=dict(size=8, color='green'),
            customdata= tree_related_311[['request_number', 'address', 'reason', 'status', 'date_created']].values.tolist()
        )
    )


    fig.update_layout(
        map=dict(center=new_orleans_center, zoom=10, style="open-street-map"),
        # autosize = True,
        width = 1100,
        height= 900,
        dragmode = 'pan',
        clickmode = 'event+select',
        hovermode='closest'
    )



    plot_html = pio.to_html(fig, full_html=False)

    return render(request, 'index.html', {'plot_html': plot_html})
