#!/usr/bin/python3

import simplegexf


gexf = simplegexf.Gexf('file.gexf')

try:
    graph = gexf.graphs[0]
except IndexError:
    graph = gexf.add_graph(defaultedgetype="directed")

graph.define_attributes([
    ('name', 'string'),
    ('description', 'string'),
    ('weight', 'integer'),
])

graph.define_attributes([
    ('rel_type', 'string'),
], _class='edge')

tag_list = [
    {
        'id': 'c6fa996d-8593-484d-b067-69bc828bbeba',
        'name': 'Test Tag',
        'description': "Fairy penguins citylink, east brunswick club trams",
        'weight': 13,
        'parents': [],  # List of UUIDs

    }
]

# Create Nodes:
for tag in tag_list:
    try:
        node = graph.get_node(tag['id'])
    except KeyError:
        node = graph.create_node(tag['id'])

    # even...
    node = graph.get_or_create_node(tag['id'])

    node.attributes.update([

        ('name', tag['name']),
        ('description', tag['description']),
        ('weight', tag['weight']),
    ])

# Create Edges:
for tag in tag_list:
    for parent_id in tag.get('parents', []):
        try:
            edge = graph.get_edge(parent_id, tag['id'])
        except KeyError:
            edge = graph.create_edge(parent_id, tag['id'])

        # even...
        edge = graph.get_or_create_edge(parent_id, tag['id'])

        edge.attributes['rel_type'] = 'parents'