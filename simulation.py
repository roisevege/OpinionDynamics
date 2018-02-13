
import math
from models import DeffuantModel
import networkx as nx  # networkx 2.x
import numpy as np
import os
import pickle
from copy import deepcopy
class Node(object):

  def __init__(self, opinion):
    # opinion can be binary, float, or a list of number.
    self.opinion = opinion

class OpinionSim(object):

  def __init__(self, model, num_nodes, directory, num_edges=None, **kwargs):
    self.graph = None
    self.num_nodes = num_nodes
    self.num_edges = num_edges
    self.params = kwargs
    if model == 'deffuant':
      self.model = DeffuantModel(self.graph, kwargs)
    self.generateGraph(kwargs)
    self.directory = directory
    os.mkdir(self.directory)
    os.mkdir(os.path.join(self.directory, 'opinion_data'))
    os.mkdir(os.path.join(self.directory, 'network_data'))
    os.mkdir(os.path.join(self.directory, 'analysis'))

    # output params
    with open('%s/param' % self.directory, 'w') as fd:
      fd.write("num_nodes:%s", self.num_nodes)
      fd.write("num_edges:%s", self.num_edges)
      fd.write("model:%s", model)
      for k,v in kwargs.items():
        fd.write("%s:%s" % (k, v))

  def _connected_random_network(self, n, m):
    G = nx.gnm_random_graph(n=n,m=m)
    degree = dict(G.degree())
    for no_degree_node in [k for k, v in degree.items() if v == 0]:
      target_node = np.random.choice([k for k, v in degree.items() if v >= 2])
      i = np.random.choice(len(G.edges(target_node)))
      target_edge = list(G.edges(target_node))[i]
      G.remove_edge(target_edge[0], target_edge[1])
      G.add_edge(no_degree_node, target_edge[1])
    return G

  def _generateTwoComm(self, seg):
    num_node1 = int(self.num_nodes/2)
    num_node2 =  self.num_nodes - num_node1
    theor_cross_edge = 2*num_node1*num_node2/(1.0*(num_node1+num_node2)*(num_node1+num_node2-1))
    theor_cross_edge *= self.num_edges
    cross_edges = seg * theor_cross_edge
    num_edge1 = int(0.5*(self.num_edges - cross_edges))
    num_edge2 = self.num_edges - cross_edges - num_edge1

    # check whether it's valid two community
    ratio1 = num_edge1/float(num_node1)
    ratio2 = num_edge2/float(num_node2)
    if ratio1 < 1 or ratio2 < 1:
      raise Exception("this seg_val(%s) doesn't work in current network size" % seg)
    graph1 = self._connected_random_network(num_node1, num_edge1)
    graph2 = self._connected_random_network(num_node2, num_edge2)

    self.graph = deepcopy(graph1)
    nx.set_node_attributes(self.graph, 0, 'init_community')

    graph2_edges = list(graph2.edges())
    for i in range(num_edge2):
      graph2_edges[i] = (graph2_edges[i][0]+num_node1, graph2_edges[i][1]+num_node1)

    self.graph.add_edges_from(graph2_edges)
    c2_nodes = set()
    for node, n_dict in self.graph.nodes(data=True):
      if 'init_community' not in n_dict:
        c2_nodes.add(node)

    for node in c2_nodes:
      self.graph[node]['init_community'] = 1




  def generateGraph(self, **kwargs):
    ''' initialize self.graph
    '''
    network_structure = kwargs['structure']
    if network_structure == 'lattice2D':
      m = math.sqrt(self.num_nodes)
      self.graph = nx.grid_2d_graph(m, m)
      self.num_edges = self.graph.num_of_edges()
    elif network_structure == 'scaleFree':
      assert self.num_edges
      self.graph = nx.barabasi_albert_graph(self.num_nodes, self.num_edges)
    elif network_structure == 'smallWorld':
      self.graph = nx.connected_watts_strogatz_graph(self.num_nodes,
                                                     self.params['k'],
                                                     self.params['p'])
      self.num_edges = self.graph.num_of_edges()
    elif network_structure == 'randomNetwork':
      assert self.num_edges
      self.graph = self._connected_random_network(self.num_nodes, self.num_edges)
    elif network_structure == 'twoCommunities':
      self._generateTwoComm(kwargs['seg'])
    else:
      raise Exception('network is not initialized...')

  def simulation(self, iterations, gap):
    count = 0 
    for i in iterations:
      self.model.opinionUpdate()
      count += 1
      if count == gap:
        self.outputGraph(i)
        count = 0

    self.outputGraph(iterations)

  def outputGraph(self, iteration):
    '''output graph with opinions'''
    nx.write_gexf(self.graph, '%s/network_data/%s' % (self.directory,
                                                      iteration))
    opinion_dict = nx.get_node_attributes(self.graph, 'opinion')
    with open("%s/opinion_data/%s.pkl" % (self.directory, iteration), 'wb') as pickleFile:
      pickle.dump(opinion_dict, pickleFile)
