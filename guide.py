################################ GUIDE MODULE ##################################
#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This is the python script of the guide module. This module contains all the
functions needed to deal with city graphs, and manage the algorithms to perform
an efficient treatement of these graphs. The module is mostly based on osmnx and
networkx packages.

Eventhough this module has been built to be perfectly suitable with the
bot.py module, it works under the hood. This means it is not directly related with
the telegram bot and could be used on multiple purposes. """


import pickle  # standard library

import osmnx as ox  # 3rd party packages
import networkx as nx
from haversine import haversine
from staticmap import StaticMap, Line, CircleMarker


__title__ = "Guide"
__author__ = "Pau Matas and Tomás Gadea"
__maintainer__ = "Pau Matas and Tomás Gadea"
__email__ = "paumatasalbi@gmail.com and 01tomas.gadea@gmail.com"
__status__ = "Production"


# ---------------------------- Public Functions ---------------------------------


def download_graph(place):
    """ Downloads a graph from OpenStreetMap and returns it.
    Parameter is a string with the name of the location. """

    graph = ox.graph_from_place(
        place, network_type='drive', simplify=True)
    ox.geo_utils.add_edge_bearings(graph)

    # filter and delete extra info of the graph:
    for node1, info1 in graph.nodes.items():
        for node2, info2 in graph.adj[node1].items():
            edge = info2[0]
            if 'geometry' in edge:
                del(edge['geometry'])

    return graph


def save_graph(graph, filename):
    """ Saves a graph(first parameter) into a pickle file (named as second
    parameter). """

    f = open(filename, 'wb')  # open on write mode
    pickle.dump(graph, f)
    f.close()


def load_graph(filename):
    """ Returns a graph read from a pickle file."""

    f = open(filename, 'rb')  # open on read mode
    graph = pickle.load(f)
    f.close()
    return graph


def print_graph(graph):
    """ Prints nodes and edges of the graph, also a summary of its info. """

    print(nx.info(graph))

    for node1, info1 in graph.nodes.items():
        print(node1, info1)
        for node2, info2 in graph.adj[node1].items():
            print('    ', node2)
            edge = info2[0]
            print('        ', edge)


def get_directions(graph, source_location, destination_location):
    """ Returns a list of dictionaries that represents the information of the
    directions to take in order to move from point A (source_location) to point
    B (destination_location) using the shortest path."""

    src = _closest_node_to(graph, source_location)  # node represented by ID
    dst = _closest_node_to(graph, destination_location)  # node repr. by ID

    sp_nodes = nx.shortest_path(graph, src, dst)  # list of nodes repr. by ID

    return _from_path_to_directions(graph, sp_nodes, source_location,
                                    destination_location)


def plot_directions(graph, source_location, destination_location, directions,
                    filename, width=400, height=400):
    """ Plots and saves the directions from source_location to
    destination_location in a file named "filename.png"  """

    m = StaticMap(width, height)  # create a StaticMap canvas

    for i in enumerate(directions):
        # enumerate(directions) returns an enumeration object
        # from this object we are only interested in i[0]
        marker, line = _marker_line(directions, i[0])
        m.add_marker(marker)
        if line is not None:
            m.add_line(line)

    image = m.render()
    image.save(str(filename) + '.png')


def dist(a, b):
    """ Returns the geografical distance in meters from a to b, being a and b
    tuples of latitude and longitude (lat,long). """

    return haversine(a, b, unit='m')


def address_coord(address):
    """ Returns the tuple (lat,long) of a point given by an address (str). """

    try:
        return ox.geo_utils.geocode(address)

    except Exception:  # raised when address is not found in the city graph
        return None

# -------------------------------------------------------------------------------

# ---------------------------- Private Functions --------------------------------


def _closest_node_to(graph, source_location):
    """ Returns the nearest graph node (by ID) to some specified
    source_location repr. by tuple: (lat,long). """

    return ox.geo_utils.get_nearest_node(graph, source_location,
                                         method='haversine')


def _from_path_to_directions(graph, sp_nodes, source_location,
                             destination_location):
    """ Returns the transformation from a path (repr. as a list of nodes) to
    directions in their correct format: list of dictionaries. """

    # Create edge and node lists adding the additional nodes and edges
    # such that we can reach the source_location and the destination_location
    # from the graph nodes (from user to street and from street to destination):
    edges = \
        [_edges_fist_edge(graph, sp_nodes, source_location)] + \
        ox.geo_utils.get_route_edge_attributes(graph, sp_nodes) + \
        [_edges_last_edge(graph, sp_nodes, destination_location)]

    coord_nodes = \
        [source_location] + \
        [_id_coord(graph, node) for node in sp_nodes] + \
        [destination_location]

    # enumerate coord_nodes returns (0, (1,2)), (1, (3,4))...
    # but we are only interested in (0, 1, ...)
    # so we select i[0]

    n = len(coord_nodes)

    # Create the list of dicts (directions):
    # (Also, only interested in i[0] from enumerate)
    directions = \
        [_section(edges, coord_nodes, i[0], n)
         for i in enumerate(coord_nodes) if i[0] < n - 1]

    return directions


def _edges_fist_edge(graph, sp_nodes, source_location):
    """ Creates and returns an edge from source_location to first node in
    sp_nodes. Edge is in triplet format: (node1, node2, {'lenght':value}) """

    src = sp_nodes[0]
    src_coord = (graph.nodes[src]['y'], graph.nodes[src]['x'])
    src_length = dist(source_location, src_coord)  # haversine distance

    return (source_location, src_coord, {'length': src_length})


def _edges_last_edge(graph, sp_nodes, destination_location):
    """ Creates and returns an edge from last node in sp_npdes to
    destination_location.
    Edge is in triplet format: (node1, node2, {'lenght':value})"""

    dst = sp_nodes[-1]
    dst_coord = (graph.nodes[dst]['y'], graph.nodes[dst]['x'])
    dst_length = dist(destination_location, dst_coord)

    return (dst_coord, destination_location, {'length': dst_length})


def _id_coord(graph, node):
    """ Given a graph and a node (by ID) returns the coordinates of the node.
    Otherwise (node already in coords format) returns the same expression. """

    if not isinstance(node, tuple):
        return (graph.nodes[node]['y'], graph.nodes[node]['x'])

    return node


# --> Section functions:

def _section(edges, coord_nodes, i, n):
    """ From a list (coord_nodes) that represents a path of n nodes and a
    list (edges) of edges, returns the section (dictionary) that starts in the
    node i of coord_nodes. The section contains relevant info about the
    directions to be given in order to reach the destination of the travel. """

    section = {'angle': _get_section_angle(edges, i, n),
               'src': coord_nodes[i],
               'mid': coord_nodes[i + 1],
               'dst': _get_section_dst(coord_nodes, i, n),
               'next_name': _get_section_next_name(edges, i, n),
               'current_name': _get_street_name(edges[i]),
               'length': _get_street_length(edges[i])}

    return section


def _get_section_angle(edges, i, n):
    """ Returns the angle of the section formed by the edges i and i + 1 in the
    list of edges, if we can compute it. """

    if i >= n or i <= 1 or not 'bearing' in edges[i-1] or not 'bearing' in edges[i]:
        return None

    return edges[i]['bearing'] - edges[i-1]['bearing']


def _get_section_dst(coord_nodes, i, n):
    """ Returns the "dst" node (by coords) of the section formed by the nodes i,
    i + 1 and i + 2 in coord_nodes, if it is not out of range. """

    if i + 2 <= n - 1:
        return coord_nodes[i + 2]
    return None


def _get_section_next_name(edges, i, n):
    """ Returns the street name "next_name" of the section that corresponds to
    the street in edges[i + 1], when is not out of range. """

    if i + 2 <= n - 1:
        return _get_street_name(edges[i + 1])
    return None


def _get_street_name(edge):
    """ Returns the name of the street that corresponds to the given edge. """

    if 'name' in edge:
        if isinstance(edge['name'], str):
            return edge['name']
        elif isinstance(edge['name'], list):
            # If multiple street names, return the first name.
            return edge['name'][0]
    return None


def _get_street_length(edge):
    """ Returns the length of the street that corresponds to the given edge,
    if it exists. """

    if 'length' in edge:
        return edge['length']
    return None


# --> Plot directions sub-functions:

def _marker_line(directions, i):
    """ Returns a StaticMap line and marker with different features depending on
    the type of the section given. Section is obtained selecting the i-th dict
    in directions. """

    # Get coords (lat1,long1), (lat2,long2) of two consecutive nodes (1 and 2):
    lat1 = directions[i]['src'][0]
    long1 = directions[i]['src'][1]

    lat2 = directions[i]['mid'][0]
    long2 = directions[i]['mid'][1]

    # Compute the vector from node1 to node2 as its difference of coords:
    diff = ((long1, lat1), (long2, lat2))

    n = len(directions)

    m_color, m_width = _get_marker_feature(i, n)
    l_color, l_width = _get_line_feature(i, n)

    # CircleMarker needs coords, color and with of marker.
    marker = CircleMarker((long1, lat1), m_color, m_width)
    # Line needs a vector, color and with for the line.
    line = None if l_color is None else Line(diff, l_color, l_width)

    return marker, line


def _get_marker_feature(i, n):
    """ Returns the color and width of the marker depending on his position (i)
    in the path of the travel: Blue for extrema, and red for middle markers."""

    if i == 0 or i == n - 1:
        return 'blue', 20
    return 'red', 10


def _get_line_feature(i, n):
    """ Returns the color and width of the line with position 'i' in the path of
    the travel. Returns None, None if the line shouldn't be printed. """

    if i == n - 1:
        return None, None
    return 'red', 4


################################################################################
