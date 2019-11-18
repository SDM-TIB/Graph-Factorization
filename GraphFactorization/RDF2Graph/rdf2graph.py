import collections
import itertools

import pandas as pd
import time

from graph import Graph2
from itertools import combinations
from rdflib import Graph, URIRef, Literal

def record_timestamp(func):
    """Record timestamp before and after call of `func`."""
    def deco(self):
        """self.timestamps[func.__name__ + '_in'] = time.time()"""
        self.timestamps[func.__name__ + '_in'] = int(time.time() * 1000.0)
        func(self)
        # self.timestamps[func.__name__ + '_out'] = time.time()
        self.timestamps[func.__name__ + '_out'] = int(time.time() * 1000.0)
    return deco

class rdf2Graph(object):
    """`rdf2graph` algorithm."""

    def __init__(self,
                 rdf_file_name,
                 graph_file_name
                 ):
        """Initialize gSpan instance."""
        self.rdf_file_name = rdf_file_name
        self.graph_file_name = graph_file_name
        self.graphs = dict()
        self._frequent_size1_subgraphs = list()
        self._frequent_subgraphs = list()
        self._vertex_counter = itertools.count()
        self.timestamps = dict()
        self._edge_counter = itertools.count()
        self._vertex_dict = {}


    def time_stats(self):
        """Print stats of time."""
        #func_names = ['_read_graphs', 'run']
        func_names = ['run']
        time_deltas = collections.defaultdict(float)
        for fn in func_names:
            time_deltas[fn] = round(self.timestamps[fn + '_out'] - self.timestamps[fn + '_in'],2)

        #print('Read:\t{} s'.format(time_deltas['_read_graphs']))
        #print('Mine:\t{} s'.format(
            #time_deltas['run'] - time_deltas['_read_graphs']))
        print('Total:\t{} ms'.format(time_deltas['run']))
        return self



    @record_timestamp
    def run(self):
        rdfGraph = Graph()
        result = rdfGraph.parse(self.rdf_file_name, format="n3")
        g = Graph2(0, is_undirected=False)

        for s, p, o in rdfGraph:
            print("subject : ", s)
            print("predicate : ", p)
            print("object : ", o)
            if not s in self._vertex_dict:
                vid = next(self._vertex_counter)
                self._vertex_dict[s] = vid
                g.add_vertex(vid, s)
            if not o in self._vertex_dict:
                vid = next(self._vertex_counter)
                self._vertex_dict[o] = vid
                g.add_vertex(vid, o)
            eid = next(self._edge_counter)
            g.add_edge(eid, self._vertex_dict[s], self._vertex_dict[o], p)
        text_file = open(self.graph_file_name, "w")
        text_file.write("t # 0\n")
        text_file.write(g.display())
        text_file.write("\nt # -1")
        text_file.flush()
        text_file.close()
        print("graph has %s statements." % len(rdfGraph))
