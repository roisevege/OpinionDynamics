import networkx as nx  # networkx 2.x
import random

class DeffuantModel(object):

  def __init__(self, graph, **kwargs):
    self.G = graph
    self.nodes = list(self.G.nodes())
    self.edges = list(self.G.edges())
    self.mu = kwargs['mu']  # convergence param
    self.d = kwargs['d']  # threshold

  def opinionUpdate(self, select_strategy='random'):
    if select_strategy == 'random':
      n1 = random.choice(self.nodes)
      n2 = n1
      while n2 == n1:
        n2 = random.choice(self.nodes)

    elif select_strategy == 'neighbor':
      n1, n2 = random.choice(list(self.G.edges()))

    o1 = self.G.nodes[n1]['opinion']
    o2 = self.G.nodes[n2]['opinion']
    if abs(o1-o2) <= self.d:
      self.G.nodes[n1]['opinion'] += self.mu*(o2-o1)
      self.G.nodes[n2]['opinion'] += self.mu*(o1-o2)


