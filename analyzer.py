import networkx  # networkx 2.x


class Analyzer(object):

  def __init__(self, folder):
    self.G = None
    self.folder = folder
    pass

  def opinionEvolve(self):
    pass

  def networkVisualization(self, iteration):
    pass

  def TopoInfluence(self):
    """influence to segregation(distance, opinion)"""
    pass

  def ParamInfluence(self, param):
    """influence to segregation(distance, opinion)"""
    pass
