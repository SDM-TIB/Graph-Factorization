import collections
import os
import sys
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

class rdfClass2Graph(object):
    """`rdf2graph` algorithm."""

    def __init__(self,
                 rdf_folder_name,
                 rdf_format,
                 class_property_file_name,
                 graph_folder_name,
                 output_folder_name
                 ):
        """Initialize gSpan instance."""
        self.rdf_folder_name = rdf_folder_name
        self.rdf_format = rdf_format
        self.class_property_file_name = class_property_file_name
        self.graph_folder_name = graph_folder_name
        self.output_folder_name=output_folder_name
        self.graphs = dict()
        self._frequent_size1_subgraphs = list()
        self._frequent_subgraphs = list()
        self._vertex_counter = itertools.count()
        self.timestamps = dict()
        self._edge_counter = itertools.count()
        self._vertex_dict = {}
        self.subjectsSet= set()
        self.g = Graph2(0, is_undirected=False)
        self.className=""


    def time_stats(self):
        """Print stats of time."""
        #func_names = ['_read_graphs', 'run']
        func_names = ['run']
        time_deltas = collections.defaultdict(float)
        for fn in func_names:
            time_deltas[fn] = round(self.timestamps[fn + '_out'] - self.timestamps[fn + '_in'],2)
        print('Total:\t{} ms'.format(time_deltas['run']))
        if not os.path.exists(self.output_folder_name+'/rdf2GraphResult'):
            result_file = open(self.output_folder_name+'/rdf2GraphResult', 'a+')
            result_file.write("%s\t%s\t%s" % ('Approach','Class','Exe.Time(ms)'))
            result_file.write("\n")
        else:
            result_file = open(self.output_folder_name + '/rdf2GraphResult', 'a+')
        result_file.write("%s\t%s\t%s" % ('rdf2Graph',self.className, format(time_deltas['run'])))
        result_file.write("\n")
        result_file.flush()
        result_file.close()
        return self



    @record_timestamp
    def run(self):
        filelist = os.listdir(self.rdf_folder_name)
        with open(self.class_property_file_name, 'r') as propertyfile:
            self.class_properties = propertyfile.read()
        line_parts = self.class_properties.split("\t")
        class_name = line_parts[0]
        class_name = class_name.replace('<', '').replace('>', '')
        self.className=class_name.split("#")[1]
        print("Class : ", class_name)

        for f in filelist:
            rdfGraph = Graph()
            rdfGraph.parse(self.rdf_folder_name+"/"+f, format=self.rdf_format)
            for s, p, o in rdfGraph:
                if not s in self._vertex_dict:
                    vid = next(self._vertex_counter)
                    self._vertex_dict[s] = vid
                    self.g.add_vertex(vid, s)
                if not o in self._vertex_dict:
                    vid = next(self._vertex_counter)
                    self._vertex_dict[o] = vid
                    self.g.add_vertex(vid, o)
                eid = next(self._edge_counter)
                self.g.add_edge(eid, self._vertex_dict[s], self._vertex_dict[o], p)
        gStr = self.g.display()
        if gStr:
            with open(self.graph_folder_name+"/"+self.className+"graph.data", "w+") as text_file:
                text_file = open(self.graph_folder_name+"/"+self.className+"graph.data", "w")

                text_file.write("t # 0\n")
                text_file.write(self.g.display())
                text_file.write("\nt # -1")
                text_file.flush()
                text_file.close()


    @record_timestamp
    def run2(self):
        filelist = os.listdir(self.rdf_folder_name)
        with open(self.class_property_file_name, 'r') as propertyfile:
            self.class_properties = propertyfile.read()
        line_parts = self.class_properties.split("\t")
        SP = eval(line_parts[1])
        class_name = line_parts[0]
        class_name = class_name.replace('<', '').replace('>', '')
        self.className = class_name.split("#")[1]
        # print("Properties : ", SP)
        print("Class : ", class_name)

        for f in filelist:
            # with open(inputdir + , 'r') as f:
            # print("Reading file : ", f)
            rdfGraph = Graph()
            rdfGraph.parse(self.rdf_folder_name + "/" + f, format=self.rdf_format)
            # print("Collecting subjects from ", f)
            for s, p, o in rdfGraph:
                # Match without angle brakets
                # print("class_name : ", str(class_name))
                # print("remove < : ", str(class_name).replace('<', '').replace('>', ''))
                # print("remove > : ", str(class_name).replace('>', ''))
                if str(p) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' and str(o) == class_name:
                    self.subjectsSet.add(s)
                    # print("class matched subject is : ",s)
            # print("Generating graphs for ", f)
            for s, p, o in rdfGraph:
                if str(p) != 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
                    if s in self.subjectsSet:
                        # or o in self.subjectsSet:
                        if not s in self._vertex_dict:
                            vid = next(self._vertex_counter)
                            self._vertex_dict[s] = vid
                            self.g.add_vertex(vid, s)
                        if not o in self._vertex_dict:
                            vid = next(self._vertex_counter)
                            self._vertex_dict[o] = vid
                            self.g.add_vertex(vid, o)
                        eid = next(self._edge_counter)
                        self.g.add_edge(eid, self._vertex_dict[s], self._vertex_dict[o], p)
        gStr = self.g.display()
        if gStr:
            with open(self.graph_folder_name + "/" + self.className + "graph.data", "w+") as text_file:
                text_file = open(self.graph_folder_name + "/" + self.className + "graph.data", "w")

                text_file.write("t # 0\n")
                # text_file.write("hello hi  \n")
                # print("Writing graph to file")
                # g.display()
                # text_file.write(self.g.display())
                text_file.write(self.g.display())
                text_file.write("\nt # -1")
                text_file.flush()
                text_file.close()
        # print("graph has %s statements." % len(rdfGraph))
        # rdfGraph = Graph()
        # result = rdfGraph.parse(self.rdf_file_name, format="n3")
        # g = Graph2(0, is_undirected=False)
        #
        #
        #
        # for s, p , o in rdfGraph:
        #     # Match without angle brakets
        #     if str(p) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' and str(o)==class_name:
        #         self.subjectsSet.add(s)
        #         print("class matched subject is : ",s)
        #
        # for s, p, o in rdfGraph:
        #     if s in self.subjectsSet:
        #         #or o in self.subjectsSet:
        #         if not s in self._vertex_dict:
        #             vid = next(self._vertex_counter)
        #             self._vertex_dict[s] = vid
        #             g.add_vertex(vid, s)
        #         if not o in self._vertex_dict:
        #             vid = next(self._vertex_counter)
        #             self._vertex_dict[o] = vid
        #             g.add_vertex(vid, o)
        #         eid = next(self._edge_counter)
        #         g.add_edge(eid, self._vertex_dict[s], self._vertex_dict[o], p)
        # text_file = open(self.graph_file_name, "w")
        # text_file.write("t # 0\n")
        # text_file.write(g.display())
        # text_file.write("\nt # -1")
        # text_file.close()
        # print("graph has %s statements." % len(rdfGraph))
        # print("Total instances : ", len(self.subjectsSet))