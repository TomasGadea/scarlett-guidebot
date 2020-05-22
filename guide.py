import networkx as nx
import osmnx as ox
from haversine import haversine
from staticmap import StaticMap, Line, CircleMarker
import pickle


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



def get_directions(graph, source_location, destination_location):
    """ Return a list of nodes that represents the shortest path from the closest node to source_location
        to the closest node to destination_location."""
    src = closest_node_to(graph, source_location)
    dst = closest_node_to(graph, destination_location)

    sp_nodes = nx.shortest_path(graph, src, dst)  # nodes with ID

    return from_path_to_directions(graph, sp_nodes, source_location, destination_location)
    # returns list of dict.


def closest_node_to(graph, source_location):
    """ Return the graph node nearest to some specified source_location:
        (lat, lng) """

    return ox.geo_utils.get_nearest_node(graph, source_location, method='haversine')


def from_path_to_directions(graph, sp_nodes, source_location, destination_location):
    """ Returns the transformation from a path (represented as a list of nodes)
        to directions in their correct format """

    src = sp_nodes[0]
    dst = sp_nodes[-1]

    src_coord = (graph.nodes[src]['y'], graph.nodes[src]['x'])
    dst_coord = (graph.nodes[dst]['y'], graph.nodes[dst]['x'])

    src_length = dist(source_location, src_coord)
    dst_length = dist(destination_location, dst_coord)

    # afegim les arestes i nodes extres per a arribar tant a l'usuari com al
    # destí per a facilitar-nos la feina a l'hora de transformar a seccions
    # recorrent una sola llista i no diferents trossos

    edges = \
        [(source_location, src_coord, {'length': src_length})] + \
        ox.geo_utils.get_route_edge_attributes(graph, sp_nodes) + \
        [(dst_coord, destination_location, {'length': dst_length})]

    coord_nodes = \
        [source_location] + \
        [id_coord(graph, node) for node in sp_nodes] + \
        [destination_location]

    n = len(coord_nodes)

    # enumerate coord_nodes returns (0, (1,2)), (1, (3,4))...
    # but we are only interested in (0, 1, ...)
    # so we select i[0]
    directions = \
        [section(edges, coord_nodes, i[0], n)
         for i in enumerate(coord_nodes) if i[0] < n - 1]

    return directions  # is a list of dictionaries


def id_coord(graph, node):
    # id_to_coord
    """ Given a graph and a node (in form of coordinates or id) returns the geo
        coordinates of that node in form of a tuple """
    if not isinstance(node, tuple):
        return (graph.nodes[node]['y'], graph.nodes[node]['x'])

    return node


def section(edges, coord_nodes, i, n):
    """ From a list that represents a path of n nodes and its relative in edges
        returns the section (dictionary) that starts in the node i of the list """

    section = {'angle': angle(edges, i, n),
               # podriem fer directions[i] ja que directions ja és la llista de tuples?
               'src': coord_nodes[i],
               'mid': (coord_nodes[i + 1])}

    if i + 2 <= n - 1:
        section['dst'] = coord_nodes[i + 2]

        section['next_name'] = get_name_of(edges[i + 1])

    else:
        section['dst'] = None
        section['next_name'] = None

    section['current_name'] = get_name_of(edges[i])

    if 'length' in edges[i]:
        section['length'] = edges[i]['length']
    else:
        section['length'] = None

    return section


def get_name_of(street):
    """ Returns the name of the street represented by the edge street if exists """
    if 'name' in street:
        if isinstance(street['name'], str):
            return street['name']
        elif isinstance(street['name'], list):
            return street['name'][0]
    return None


def angle(edges, i, n):
    """ Returns the angle of edges i and i + 1 in edges if we can
        calculate it. """
    if i >= n-1 or not 'bearing' in edges[i] or not 'bearing' in edges[i + 1]:
        return None
    return edges[i + 1]['bearing'] - edges[i]['bearing']


def plot_directions(graph, source_location, destination_location, directions, filename, width=400, height=400):
    """ Plots and saves the sections from source_location to destination_location described
        by directions in a file named filename.png """

    m = StaticMap(width, height)

    for i in enumerate(directions):

        # we are only interested in i[0]
        marker, line = marker_line(directions, i[0])
        m.add_marker(marker)
        if line is not None:
            m.add_line(line)

    image = m.render()
    image.save(str(filename) + '.png')


def marker_line(directions, i):
    """ Returns one line and marker with diferent caracteristics depending on
        the type of the section given """

    lat1 = directions[i]['src'][0]
    long1 = directions[i]['src'][1]

    lat2 = directions[i]['mid'][0]
    long2 = directions[i]['mid'][1]

    diff = ((long1, lat1), (long2, lat2))

    n = len(directions)

    if i == 0:
        marker = CircleMarker((long1, lat1), 'blue', 20)
        line = Line(diff, 'red', 4)
    elif i == n - 1:
        marker = CircleMarker((long1, lat1), 'blue', 20)
        line = None
    else:
        marker = CircleMarker((long1, lat1), 'red', 10)
        line = Line(diff, 'red', 4)

    return marker, line


def dist(a, b):
    """ Returns the geografical distance from a=(lat,long) to b=(lat,long)"""
    return haversine(a, b, unit='m')


def address_coord(address):
    # from_address
    """ Returns (lat, long) of a point given by an address """
    return ox.geo_utils.geocode(address)
