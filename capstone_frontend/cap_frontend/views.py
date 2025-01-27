from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import Calls

import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

def home(request):
    return render(request, 'index.html')
    #template = loader.get_template('home.html')
    #return HttpResponse(template.render({}, request))

new_orleans_center = {"lon": -90.07, "lat": 29.95}


# Add dummy data to the map of NOLA
def index(request):

    dummy_data = Calls.objects.all()

    data = pd.DataFrame(list(dummy_data.values()))
    data['text'] = "Request Number:  " + data['request_number'].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=data['latitude'],
            lon=data['longitude'],
            text=data['text'],
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

#def data_view(request):#
    #data = Calls.objects.all()  # Fetch all data from the DummyData table
    #return render(request, 'my_app/data_template.html', {'data': data})