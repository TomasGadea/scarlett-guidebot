import networkx as nx
import osmnx as ox
from haversine import haversine
from staticmap import StaticMap, Line, CircleMarker
import pickle
import matplotlib.pyplot as plt


def download_graph(place):
    """ Downloads a graph from OpenStreetMap and returns it. Parameter is a
        string with the name of the location. """

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
    """ Saves a graph (passed as first parameter) into a pickle file (named as
        second parameter). """

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
    """ Represents graphicaly the graph passed as parameter and summarizes its
        information. """

    print(nx.info(graph))

    # for node1, info1 in graph.nodes.items():
    #     print(node1, info1)
    #     for node2, info2 in graph.adj[node1].items():
    #         print('    ', node2)
    #         edge = info2[0]
    #         print('        ', edge)
    #
    # ox.plot_graph(graph)
    # plt.show()


def get_directions(graph, source_location, destination_location):
    """ Return a list of nodes that represents the shortest path from the closest node to source_location
        to the closest node to destination_location."""
    src = closest_node_to(graph, source_location)
    dst = closest_node_to(graph, destination_location)

    return nx.shortest_path(graph, src, dst)  # nodes with ID


def closest_node_to(graph, source_location):
    """ Return the graph node nearest to some specified source_location:
        (lat, lng) """

    return ox.geo_utils.get_nearest_node(graph, source_location, method='haversine')


def from_path_to_directions(graph, sp_nodes, source_location, destination_location):
    """ Returns the transformation from a path (represented as a list of nodes)
        to directions in their correct format """

    src = closest_node_to(graph, source_location)
    dst = closest_node_to(graph, destination_location)

    # afegim les arestes i nodes extres per a arribar tant a l'usuari com al
    # destí per a facilitar-nos la feina a l'hora de transformar a seccions
    # recorrent una sola llista i no diferents trossos

    sp_edges = [(source_location, src, {'length': src_length})] + ox.geo_utils.get_route_edge_attributes(
        graph, sp_nodes) + [(dst, destination_location, {'length': dst_length})]
    sp_nodes = [source_location] + \
        [id_to_coord_tuple(graph, node)
         for node in sp_nodes] + [destination_location]

    n = len(sp_nodes)
    directions = [section(graph, sp_edges, sp_nodes, i, n) for i, node
                  in enumerate(sp_nodes) if i < n - 1]
    return directions  # is a list of dictionaries


def section(graph, sp_edges, sp_nodes, i, n):
    """ From a list that represents a path of n nodes and its relative in edges
        returns the section (dictionary) that starts in the node i of the list """
    section = {'angle': angle(sp_edges, i, n),
               # podriem fer sp_nodes[i] ja que sp_nodes ja és la llista de tuples?
               'src': (sp_nodes[i][0], sp_nodes[i][1]),
               'mid': (sp_nodes[i + 1][0], sp_nodes[i + 1][1])}

    if i + 2 <= n - 1:
        section['dst'] = (sp_nodes[i + 2][0], sp_nodes[i + 2][1])

        if 'name' in sp_edges[i + 1]:
            section['next_name'] = sp_edges[i + 1]['name']
        else:
            section['next_name'] = None
    else:
        section['dst'], section['next_name'] = None, None

    if 'name' in sp_edges[i]:
        section['current_name'] = sp_edges[i]['name']
    else:
        section['current_name'] = None

    if 'length' in sp_edges[i]:
        section['length'] = sp_edges[i]['length']
    else:
        section['length'] = None

    return section


def id_to_coord_tuple(graph, node):
    """ Given a graph and a node (in form of coordinates or id) returns the geo
        coordinates of that node in form of a tuple """
    if not isinstance(node, tuple):
        return (graph.nodes[node]['y'], graph.nodes[node]['x'])

    return node


def angle(sp_edges, i, n):
    """ Returns the angle of edges i and i + 1 in sp_edges if we can
        calculate it. """
    if i >= n-1 or not 'bearing' in sp_edges[i] or not 'bearing' in sp_edges[i + 1]:
        return None
    return sp_edges[i + 1]['bearing'] - sp_edges[i]['bearing']


def plot_directions(graph, source_location, destination_location, directions, filename, width=400, height=400):
    """ Plots and saves the route from source_location to destination_location described
        by directions in a file named filename.png """
    route = from_path_to_directions(
        graph, directions, source_location, destination_location)

    m = StaticMap(width, height)
    for section in route:

        marker, line = marker_and_line_depending_on_section_type(section)
        m.add_marker(marker)
        m.add_line(line)

        if section['dst'] is None:
            m.add_marker(CircleMarker(
                (section['mid'][1], section['mid'][0]), 'blue', 20))

    image = m.render()
    image.save(filename + '.png')


def marker_and_line_depending_on_section_type(section):
    """ Returns one line and marker with diferent caracteristics depending on
        the type of the section given """
    # section['src'] ja es una tupla?
    src = (section['src'][1], section['src'][0])
    dst = (section['mid'][1], section['mid'][0])
    coordinates = [[src[0], src[1]], [dst[0], dst[1]]]

    # pot ser que marqui blau en mig del recorregut? (Passem per carrerons sense nom)
    if section['current_name'] is None:
        if section['next_name'] is not None:
            marker = CircleMarker(src, 'blue', 20)
            line = Line(coordinates, 'blue', 4)
        else:
            marker = CircleMarker(src, 'red', 10)
            line = Line(coordinates, 'blue', 4)
    else:
        marker = CircleMarker(src, 'red', 10)
        line = Line(coordinates, 'red', 4)
    return marker, line


def dist(a, b):
    return haversine(a, b, unit='m')


def from_address(message):
    return ox.geo_utils.geocode(message)
