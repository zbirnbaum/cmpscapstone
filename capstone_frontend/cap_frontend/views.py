from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import Calls, Trees

import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

def home(request):
    return render(request, 'index.html')
    #template = loader.get_template('home.html')
    #return HttpResponse(template.render({}, request))

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
       'Christmas Tree Recycle Pick Up'])]

    trees = Trees.objects.values()
    treesdata = pd.DataFrame(list(trees))

    tree_related_311['text'] = "Request Number:  " + tree_related_311['request_number'].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=tree_related_311['latitude'],
            lon=tree_related_311['longitude'],
            text=tree_related_311['text'],
            mode='markers',
            marker=dict(size=6, color='green'),
            name='Open Tree-Related 311 Reports'
        )
    )

    fig.update_layout(
        mapbox=dict(center=new_orleans_center, zoom=10, style="open-street-map")
    )

    plot_html = pio.to_html(fig, full_html=False)

    return render(request, 'index.html', {'plot_html': plot_html})


