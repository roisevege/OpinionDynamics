import matplotlib.pyplot as plt
import networkx as nx  # networkx 2.x
import os
import pickle

class Analyzer(object):

  def __init__(self, folder, time):
    self.folder = folder
    self.time = time # a list 
    self.num_nodes = None
    self.num_edges = None

  def opinionEvolve(self):
    plt.clf()
    plt.axis([0,self.time[-1],0,1])
    plt.xlabel('t')
    plt.ylabel('o')
    for c_time in self.time:
      opinions = None
      with open('%s/opinion_data/%s' % (self.folder, c_time), "rb") as fd:
        opinions = pickle.load(fd)
      x = [c_time for i in range(len(opinions))]
      l = plt.plot(x, opinions, 'ro', markersize=1)
    plt.savefig('%s/analysis/opinionEvolve.png' % self.folder)

  def opinionDistribution(self, c_time):
    plt.clf()
    with open('%s/opinion_data/%s' % (self.folder, c_time), "rb") as fd:
      opinions = pickle.load(fd)
    print(opinions)
    plt.hist(opinions, range=(0, 1))
    plt.savefig('%s/analysis/opinionDist%s.png' % (self.folder, c_time))

  def networkVisualization(self, iteration):
    pass

  def TopoInfluence(self):
    """influence to segregation(distance, opinion)"""
    pass

  def ParamInfluence(self, param):
    """influence to segregation(distance, opinion)"""
    pass

folder = 'Data_2018021322031120'
files = os.listdir('%s/opinion_data' % folder)
times = []
for f in files:
  try:
    times.append(int(f))
  except:
    continue
times.sort()

analyzor = Analyzer(folder, times)
analyzor.opinionEvolve()
#analyzor.opinionDistribution(times[-1])