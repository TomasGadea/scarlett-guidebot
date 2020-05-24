################################ GUIDE MODULE ##################################

import networkx as nx
import osmnx as ox
from haversine import haversine
from staticmap import StaticMap, Line, CircleMarker
import pickle

#---------------------------- Public Functions ---------------------------------

def download_graph(place):
    """ Downloads a graph from OpenStreetMap and returns it. Parameter is a string with the name of the location. """

    graph = ox.graph_from_place(
        place, network_type='drive', simplify=True)
    ox.geo_utils.add_edge_bearings(graph)

    for node1, info1 in graph.nodes.items():
        for node2, info2 in graph.adj[node1].items():
            edge = info2[0]
            if 'geometry' in edge:
                del(edge['geometry'])

    return graph

def save_graph(graph, filename):
    """ Saves a graph (passed as first parameter) into a pickle file (named assecond parameter). """

    f = open(filename, 'wb')
    pickle.dump(graph, f)
    f.close()

def load_graph(filename):
    """ Returns a graph read from a pickle file."""

    f = open(filename, 'rb')
    graph = pickle.load(f)
    f.close()
    return graph

def print_graph(graph):
    """ Represents graphicaly the graph passed as parameter and summarizes its information. """

    print(nx.info(graph))

    for node1, info1 in graph.nodes.items():
        print(node1, info1)
        for node2, info2 in graph.adj[node1].items():
            print('    ', node2)
            edge = info2[0]
            print('        ', edge)

def get_directions(graph, source_location, destination_location):
    """ Returns a list of dictionaries that represents the information of the directions to go over the shortest path from the source_location to the destination_location."""

    src = _closest_node_to(graph, source_location)
    dst = _closest_node_to(graph, destination_location)

    sp_nodes = nx.shortest_path(graph, src, dst)  # nodes with ID

    return _from_path_to_directions(graph, sp_nodes, source_location, destination_location)

def plot_directions(graph, source_location, destination_location, directions, filename, width=400, height=400):
    """ Plots and saves the directions from source_location to destination_location in a file named filename.png. """

    m = StaticMap(width, height)

    for i in enumerate(directions):

        # we are only interested in i[0]
        marker, line = _marker_line(directions, i[0])
        m.add_marker(marker)
        if line is not None:
            m.add_line(line)

    image = m.render()
    image.save(str(filename) + '.png')

def dist(a, b):
    """ Returns the geografical distance from a=(lat,long) to b=(lat,long). """

    return haversine(a, b, unit='m')

def address_coord(address):
    # from_address
    """ Returns (lat, long) of a point given by an address (str). """

    return ox.geo_utils.geocode(address)

#-------------------------------------------------------------------------------

#---------------------------- Private Functions --------------------------------

def _closest_node_to(graph, source_location):
    """ Return the graph node nearest to some specified source_location: (lat, lng). """

    return ox.geo_utils.get_nearest_node(graph, source_location, method='haversine')

def _from_path_to_directions(graph, sp_nodes, source_location, destination_location):
    """ Returns the transformation from a path (represented as a list of nodes) to directions in their correct format (dictionary). """

    # we add the additional nodes and edges such that we can reach the user and
    # the destination, making easier to transform to sections with only one list
    # and not with different pieces

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

    directions = \
        [_section(edges, coord_nodes, i[0], n)
         for i in enumerate(coord_nodes) if i[0] < n - 1]

    return directions  # is a list of dictionaries

def _edges_fist_edge(graph, sp_nodes, source_location):
    """ Returns the first edge of the list called edges in his correct form. """

    src = sp_nodes[0]
    src_coord = (graph.nodes[src]['y'], graph.nodes[src]['x'])
    src_length = dist(source_location, src_coord)

    return (source_location, src_coord, {'length': src_length})

def _edges_last_edge(graph, sp_nodes, destination_location):
    """ Returns the last edge of the list called edges in his correct form. """

    dst = sp_nodes[-1]
    dst_coord = (graph.nodes[dst]['y'], graph.nodes[dst]['x'])
    dst_length = dist(destination_location, dst_coord)

    return (dst_coord, destination_location, {'length': dst_length})

def _id_coord(graph, node):
    # id_to_coord
    """ Given a graph and a node makes sure that his format is geocords. If it isn't (is in id format) returns the coordinates. """

    if not isinstance(node, tuple):
        return (graph.nodes[node]['y'], graph.nodes[node]['x'])

    return node

#--> Section functions:

def _section(edges, coord_nodes, i, n):
    """ From a list that represents a path of n nodes (coord_nodes) and its relative in edges (edges) returns the section (dictionary) that starts in the node i of the list. """

    section = {'angle': _get_section_angle(edges, i, n),
               'src': coord_nodes[i],
               'mid': coord_nodes[i + 1],
               'dst': _get_section_dst(coord_nodes, i, n),
               'next_name': _get_section_next_name(edges, i, n),
               'current_name': _get_street_name(edges[i]),
               'length': _get_street_length(edges[i])}

    return section

def _get_section_angle(edges, i, n):
    """ Returns the angle of the section formed by the edges i and i + 1 in edges if we can calculate it. """

    if i >= n or i <= 1 or not 'bearing' in edges[i-1] or not 'bearing' in edges[i]:
        return None

    return edges[i]['bearing'] - edges[i-1]['bearing']

def _get_section_dst(coord_nodes, i, n):
    """ Returns the dst of the section formed by the nodes i, i + 1 and i + 2 in coord_nodes if it is not out of range. """

    if i + 2 <= n - 1:
        return coord_nodes[i + 2]
    return None

def _get_section_next_name(edges, i, n):
    """ Returns the next_name of the section that corresponds to the name of the street edges[i + 1] when is not out of range. """

    if i + 2 <= n - 1:
        return _get_street_name(edges[i + 1])
    return None

def _get_street_name(edge):
    """ Returns the name of the street represented by the edge edge if it exists. """

    if 'name' in edge:
        if isinstance(edge['name'], str):
            return edge['name']
        elif isinstance(edge['name'], list):
            return edge['name'][0]
    return None

def _get_street_length(edge):
    """ Returns the length of the street represented by the edge edge if it exists. """

    if 'length' in edge:
        return edge['length']
    return None

#--> Plot directions sub-functions:

def _marker_line(directions, i):
    """ Returns one line and marker with diferent characteristics depending on the type of the section given. """

    lat1 = directions[i]['src'][0]
    long1 = directions[i]['src'][1]

    lat2 = directions[i]['mid'][0]
    long2 = directions[i]['mid'][1]

    diff = ((long1, lat1), (long2, lat2))

    n = len(directions)

    m_color, m_width = _get_marker_feature(i, n)
    l_color, l_width = _get_line_feature(i, n)

    marker = CircleMarker((long1, lat1), m_color, m_width)
    line = None if l_color is None else Line(diff, l_color, l_width)

    return marker, line

def _get_marker_feature(i, n):
    """ Returns the color and width of the marker depending on his position i. """

    if i == 0 or i == n - 1:
        return 'blue', 20
    return 'red', 10

def _get_line_feature(i, n):
    """ Returns the color and width of the line or None, None (if it shouldn't be printed) depending on his position i. """

    if i == n - 1:
        return None, None
    return 'red', 4
