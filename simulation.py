
import math
from models import DeffuantModel
import networkx as nx  # networkx 2.x
import numpy as np
import os
import pandas as pd
import pickle
import random
from copy import deepcopy


class OpinionSim(object):

  def __init__(self, num_nodes, num_edges, directory, **kwargs):
    self.graph = None
    self.num_nodes = num_nodes
    self.num_edges = num_edges
    self.params = kwargs
    model = kwargs['model_dict']['model']
    self.generateGraph()
    if model == 'deffuant':
      self.model = DeffuantModel(self.graph, **kwargs['model_dict'])
    self.directory = directory
    os.mkdir(self.directory)
    os.mkdir(os.path.join(self.directory, 'opinion_data'))
    os.mkdir(os.path.join(self.directory, 'network_data'))
    os.mkdir(os.path.join(self.directory, 'analysis'))

    # output params
    with open('%s/param' % self.directory, 'w') as fd:
      fd.write("num_nodes:%s\n" % self.num_nodes)
      fd.write("num_edges:%s\n" % self.num_edges)
      fd.write("model:%s\n" % model)
      for k,v in kwargs.items():
        fd.write("%s:%s\n" % (k, v))

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
    cross_edges = int(seg * theor_cross_edge)
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
      self.graph.nodes[node]['init_community'] = 1

  def generateGraph(self):
    ''' initialize self.graph
    '''
    network_structure = self.params['structure']
    if network_structure == 'lattice2D':
      m = int(math.sqrt(self.num_nodes))
      self.graph = nx.grid_2d_graph(m, m)
      self.num_edges = self.graph.number_of_edges()
    elif network_structure == 'scaleFree':
      assert self.num_edges
      self.graph = nx.barabasi_albert_graph(self.num_nodes, self.params['scalefree_m'])
    elif network_structure == 'smallWorld':
      self.graph = nx.connected_watts_strogatz_graph(self.num_nodes,
                                                     self.params['k'],
                                                     self.params['p'])
      self.num_edges = self.graph.number_of_edges()
    elif network_structure == 'randomNetwork':
      assert self.num_edges
      self.graph = self._connected_random_network(self.num_nodes, self.num_edges)
    elif network_structure == 'twoCommunities':
      self._generateTwoComm(self.params['seg'])
    else:
      raise Exception('network is not initialized...')

    for node in list(self.graph.nodes()):
      self.graph.nodes[node]['opinion'] = np.random.uniform(0, 1.0)



  def simulation(self, iterations, gap):
    count = 0 
    self.outputGraph(0)
    for i in range(iterations):
      self.model.opinionUpdate()
      count += 1
      if count == gap:
        opinion_dict = nx.get_node_attributes(self.graph, 'opinion')
        ordered_node = sorted(list(opinion_dict.keys()))  # this operation is for easier analysis
        opinions = [opinion_dict[n] for n in ordered_node]
        with open("%s/opinion_data/%s" % (self.directory, i), 'wb') as pickleFile:
          pickle.dump(opinions, pickleFile)
        count = 0
    self.outputGraph(iterations)

  def outputGraph(self, iteration):
    '''output graph with opinions'''
    nx.write_gexf(self.graph, '%s/network_data/%s.gexf' % (self.directory,
                                                      iteration))
    opinion_dict = nx.get_node_attributes(self.graph, 'opinion')
    ordered_node = sorted(list(opinion_dict.keys()))  # this operation is for easier analysis
    opinions = [opinion_dict[n] for n in ordered_node]
    with open("%s/opinion_data/%s" % (self.directory, iteration), 'wb') as pickleFile:
      pickle.dump(opinions, pickleFile)


model = 'deffuant'
strategy = 'neighbor'
num_nodes = 100
num_edges = 400
iterations = num_nodes * 100
gap = int(0.5*num_nodes)
mu = [0.01,0.05,0.15,0.25,0.35,0.45, 0.55]  # default: mu = 0.25
d = [0.05,0.1,0.2,0.4,0.5]  # default: d = 0.4

model_dict = {"strategy": strategy, "model": model}
for c_d in d:
  if c_d != 0.4:
    continue
  now_str = pd.datetime.now().strftime('%Y%m%d%H%M%S')+'%s' % (random.randrange(10, 99))
  data_root_dir = os.path.join('Data_' + ''.join(now_str))
  print(data_root_dir)
  model_dict['mu'] = mu[3]
  model_dict['d'] = 0.4

  # small world
  '''
  p = 0.4
  k = 4
  structure = 'smallWorld'
  kwargs = {'p':p, 'k':k, 'model_dict':model_dict, 'structure':structure}
  '''

  # two communities
  '''
  structure = 'twoCommunities'
  seg = 0.6
  kwargs = {'seg':seg}
  '''
  '''
  # lattice2D
  structure = 'lattice2D'
  kwargs = {}
  '''
  '''
  #  scaleFree
  structure = 'scaleFree'
  kwargs = {'scalefree_m':int(num_edges/num_nodes)}

  '''
  #  randomNetwork
  structure = 'randomNetwork'
  kwargs = {}

  kwargs['model_dict'] = model_dict 
  kwargs['structure'] = structure

  simulator = OpinionSim(num_nodes, num_edges, data_root_dir, **kwargs)
  simulator.simulation(iterations, gap)