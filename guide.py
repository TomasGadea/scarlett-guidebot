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

    for node1, info1 in graph.nodes.items():
        print(node1, info1)
        for node2, info2 in graph.adj[node1].items():
            print('    ', node2)
            edge = info2[0]
            print('        ', edge)

    ox.plot_graph(graph)
    plt.show()


def get_directions(graph, source_location, destination_location):
    """ Return a list of maps. Each map conatins info about the section of the path (see from_path_to_directions). """

    src = closest_node_to(graph, source_location)
    src_coord = (graph.nodes[src]['y'], graph.nodes[src]['x'])
    dst = closest_node_to(graph, destination_location)
    dst_coord = (graph.nodes[dst]['y'], graph.nodes[dst]['x'])

    src_length = haversine(source_location, src_coord, unit='m')
    dst_length = haversine(destination_location, dst_coord, unit='m')

    graph.add_edges_from([(source_location, src, {'length': src_length}),
                          (dst, destination_location, {'length': dst_length})])

    shortest_path = nx.shortest_path(graph, source_location,
                                     destination_location)
    route = from_path_to_directions(graph, shortest_path)
    return route


def closest_node_to(graph, source_location):
    """ Return the graph node nearest to some specified source_location: (lat, lng) """

    return ox.geo_utils.get_nearest_node(graph, source_location, method='haversine')


def from_path_to_directions(graph, sp_nodes):
    """ Given a list of nodes in the shortest path (sp_nodes)
        returns the path in a directions format (angle, src, name, mid, ...) """

    sp_edges = ox.geo_utils.get_route_edge_attributes(graph, sp_nodes)
    sp_nodes = [id_to_coord_tuple(graph, node) for node in sp_nodes]
    n = len(sp_nodes)
    directions = [section(graph, sp_edges, sp_nodes, i, n) for i, node
                  in enumerate(sp_nodes) if i < n - 1]
    return directions


def section(graph, sp_edges, sp_nodes, i, n):
    """ ... """
    section = {'angle': angle(sp_edges, i, n),
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
    """ Given a graph and a node (in form of coordinates or id) returns the geo coordinates of that node in form of a tuple """
    if not isinstance(node, tuple):
        return (graph.nodes[node]['y'], graph.nodes[node]['x'])
    else:
        return node


def angle(sp_edges, i, n):
    """ Returns the angle of edges i and i + 1 in sp_edges if we can calculate it. """
    if i >= n-1 or not 'bearing' in sp_edges[i] or not 'bearing' in sp_edges[i + 1]:
        return None
    return sp_edges[i + 1]['bearing'] - sp_edges[i]['bearing']


def plot_directions(graph, source_location, destination_location, directions,
                    filename, width=400, height=400):
    """ Plots the route from source_location to destination_location described
        by directions in a file named filename.png """
    m = StaticMap(width, height)
    for section in directions:
        src = (section['src'][1], section['src'][0])
        dst = (section['mid'][1], section['mid'][0])
        coordinates = [[src[0], src[1]], [dst[0], dst[1]]]

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

        m.add_marker(marker)
        m.add_line(line)

        if section['dst'] is None:
            marker = CircleMarker(dst, 'blue', 20)
            m.add_marker(marker)

    image = m.render()
    image.save(filename + '.png')
