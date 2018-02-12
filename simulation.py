
from models import DeffuantModel
import networkx  # networkx 2.x
import os

class Node(object):

  def __init__(self, opinion):
    # opinion can be binary, float, or a list of number.
    self.opinion = opinion

class OpinionSim(object):

  def __init__(self, model, num_nodes, directory, num_edges=None, **kwargs):
    self.graph = None
    self.num_nodes = num_nodes
    self.num_edges = num_edges
    if model == 'deffuant':
      self.model = DeffuantModel(self.graph, kwargs)

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

  def generateGraph(self, network_structure):
    ''' initialize self.graph
    '''
    if network_structure == 'lattice2D':
      pass
    elif network_structure == 'scaleFree':
      pass
    elif network_structure == 'smallWorld':
      pass
    elif network_structure == 'randomNetwork':
      assert self.num_edges
      pass
    elif network_structure == 'twoCommunities':
      pass
    else:
      print('network is not initialized...')
      raise

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
    pass
