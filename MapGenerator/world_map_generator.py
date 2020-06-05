import os
import plotly.express as px
import pandas as pd
from collections import defaultdict
import numpy as np
from xml.dom import minidom
import xml.dom.minidom
#os.environ['path'] += r';C:\Program Files\UniConvertor-2.0rc4\dlls'
#import cairosvg

# The conversion to png is commented out because it's difficult to install in 
# Windows. The problem is the cairosvg package. To make this package work, you
# must follow the steps described here: https://stackoverflow.com/a/60220855/13686414



def load_csv(csv_name):
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

    return df2


def create_svg_temp_map(csv_name, out_name):
    df = load_csv(csv_name)

    # Create a mapping for the colors
    color_discrete_map = {
        '100': 'rgb(255, 0, 0)',
        '101': 'rgb(255, 0, 255)',
        '110': 'rgb(255, 255, 0)',
        '111': 'rgb(255, 255, 255)',
        '001': 'rgb(0, 0, 255)',
        '010': 'rgb(0, 255, 0)',
        '011': 'rgb(0, 255, 255)'
    }

    fig = px.choropleth(df, locations="iso_alpha",
                        color="category",
                        color_discrete_map=color_discrete_map
                        )

    fig.update_layout(showlegend=False, geo=dict(showlakes=False))
    fig.write_image(out_name)


def add_pattern_2_colors(dom, ID, colour1, colour2):
    parent = dom.getElementsByTagName('svg')[0]

    pattern = dom.createElement('pattern')
    pattern.setAttribute('id', ID)
    pattern.setAttribute('width', '4')
    pattern.setAttribute('height', '1')
    pattern.setAttribute('patternTransform', 'rotate(45)')
    pattern.setAttribute('patternUnits', 'userSpaceOnUse')

    rect = dom.createElement('rect')
    rect.setAttribute('width', '100%')
    rect.setAttribute('height', '100%')
    rect.setAttribute('fill', colour2)

    line = dom.createElement('line')
    line.setAttribute('style', 'stroke:%s; stroke-width:2' % colour1)
    line.setAttribute('x1', '1')
    line.setAttribute('x2', '1')
    line.setAttribute('y2', '1')

    pattern.appendChild(rect)
    pattern.appendChild(line)

    refchid = dom.getElementsByTagName('defs')[0]

    parent.insertBefore(pattern, refchid)


def add_pattern_3_colors(dom, ID, colour1, colour2, colour3):
    parent = dom.getElementsByTagName('svg')[0]

    pattern = dom.createElement('pattern')
    pattern.setAttribute('id', ID)
    pattern.setAttribute('width', '6')
    pattern.setAttribute('height', '1')
    pattern.setAttribute('patternUnits', 'userSpaceOnUse')

    rect = dom.createElement('rect')
    rect.setAttribute('width', '100%')
    rect.setAttribute('height', '100%')
    rect.setAttribute('fill', colour1)

    line1 = dom.createElement('line')
    line1.setAttribute('style', 'stroke:%s; stroke-width:2' % colour2)
    line1.setAttribute('x1', '1')
    line1.setAttribute('x2', '1')
    line1.setAttribute('y2', '1')

    line2 = dom.createElement('line')
    line2.setAttribute('style', 'stroke:%s; stroke-width:2' % colour3)
    line2.setAttribute('x1', '3')
    line2.setAttribute('x2', '3')
    line2.setAttribute('y2', '1')

    pattern.appendChild(rect)
    pattern.appendChild(line1)
    pattern.appendChild(line2)

    refchid = dom.getElementsByTagName('defs')[0]

    parent.insertBefore(pattern, refchid)


def create_map_with_strips(csv_name, out_name, colour1, colour2, colour3):
    type_file = out_name[-3:].lower()
    if type_file not in {'svg', 'png'}:
        print('Not a valid output file type')
        return
    temp_svg = 'temp.svg'
    create_svg_temp_map(csv_name, temp_svg)
    dom = minidom.parse(temp_svg)

    # Create the different patterns
    add_pattern_2_colors(dom, '12', colour1, colour2)
    add_pattern_2_colors(dom, '13', colour1, colour3)
    add_pattern_2_colors(dom, '23', colour2, colour3)
    add_pattern_3_colors(dom, '123', colour1, colour2, colour3)

    colour_pattern_map = {
        'rgb(255, 255, 0)': 'url(#12)',
        'rgb(255, 255, 255)': 'url(#123)',
        'rgb(255, 0, 0)': colour1,
        'rgb(255, 0, 255)': 'url(#13)',
        'rgb(0, 255, 0)': colour2,
        'rgb(0, 255, 255)': 'url(#23)',
        'rgb(0, 0, 255)': colour3,
    }
    # Modify the colours to use the patterns
    for country in dom.getElementsByTagName('path'):
        if country.hasAttribute('class') and country.getAttribute('class') == 'choroplethlocation':
            key = country.getAttribute('fill')
            if key in colour_pattern_map:
                country.setAttribute('fill', colour_pattern_map[key])
    # Saved the modified SVG
    dom.writexml(open(temp_svg, 'w'))

    if type_file == 'svg':
        os.rename(temp_svg, out_name)
    elif type_file == 'png':
        # Need to check the scale
        #cairosvg.svg2png(url=temp_svg, write_to=out_name, scale=5)
        #os.remove(temp_svg)
        print('Conversion to png is disabled.')


def create_map(csv_name, out_name, color1, color2, color3):
    df = load_csv(csv_name)

    # Create a mapping for the colors
    color_discrete_map = dict()
    for k in df.category.unique():
        if k in {'100', '101', '110', '111'}:
            color_discrete_map[k] = color1
        elif k in {'010', '011'}:
            color_discrete_map[k] = color2
        elif k in {'001'}:
            color_discrete_map[k] = color3

    fig = px.choropleth(df, locations="iso_alpha",
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
        if file_extension == '.csv' and not(os.path.isfile(folder + os.path.sep + taskname + '_map.png')):
            create_map(folder + os.path.sep + file, folder + os.path.sep + taskname + '_map.png', color_requester, color_volunteer, color_collaborator)
            print(folder + os.path.sep + taskname + '_map.png')


if __name__ == '__main__':
#    create_map_with_strips('test.csv', 'test.png', 'rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)')
    create_map_with_strips('test.csv', 'test.svg', 'rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)')
