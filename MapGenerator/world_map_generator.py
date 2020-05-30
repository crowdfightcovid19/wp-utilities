
import os
import plotly.express as px
import pandas as pd
from collections import defaultdict
import numpy as np


def create_map(csv_name, out_name, color1, color2, color3):
    # read the CSV
    df = pd.read_csv(csv_name, header=None, names=['c0', 'c1', 'c2'])

    d = defaultdict(lambda: [0, 0, 0])
    for i in range(3):
        for country in df['c%i' % i].unique():
            if country is not np.nan:
                d[country][i] = 1

    # Create a new DataFram with two colums
    d2 = defaultdict(list)
    for k in d:
        d2['iso_alpha'].append(k)
        d2['category'].append('%i%i%i' % tuple(d[k]))

    df2 = pd.DataFrame(d2)

    # Create a mapping for the colors
    color_discrete_map = dict()
    for k in df2.category.unique():
        if k in {'100', '101', '110', '111'}:
            color_discrete_map[k] = color1
        elif k in {'010', '011'}:
            color_discrete_map[k] = color2
        elif k in {'001'}:
            color_discrete_map[k] = color3

    fig = px.choropleth(df2, locations="iso_alpha",
                        color="category",
                        color_discrete_map=color_discrete_map
                        )

    fig.update_layout(showlegend=False, geo=dict(showlakes=False))
    fig.write_image(out_name)


def update_maps(folder):
    color_requester = 'rgb(0, 125, 125)'
    color_volunteer = 'rgb(63, 125, 255)'
    color_collaborator = 'rgb(0, 0, 255)'
    csvList = os.listdir(folder)
    for file in csvList:
        filename, file_extension = os.path.splitext(file)
        taskname = filename.split('_')[0]
        if file_extension=='.csv' and not(os.path.isfile(folder+os.path.sep+taskname+'_map.png')):               
            create_map(folder+os.path.sep+file, folder+os.path.sep+taskname+'_map.png', color_requester, color_volunteer, color_collaborator)
            print(folder+os.path.sep+taskname+'_map.png')


# if __name__ == '__main__':
#     create_map('test.csv', 'test2.png', 'rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)')
