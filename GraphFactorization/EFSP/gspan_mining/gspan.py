"""Implementation of gSpan."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import codecs
import collections
import copy
import json
import os

import itertools
import time

from graph import AUTO_EDGE_ID
from graph import Graph
from graph import VACANT_GRAPH_ID
from graph import VACANT_VERTEX_LABEL

import pandas as pd


gList = []

def record_timestamp(func):
    """Record timestamp before and after call of `func`."""
    def deco(self):
        """self.timestamps[func.__name__ + '_in'] = time.time()"""
        self.timestamps[func.__name__ + '_in'] = int(time.time() * 1000.0)
        func(self)
        #self.timestamps[func.__name__ + '_out'] = time.time()
        self.timestamps[func.__name__ + '_out'] = int(time.time() * 1000.0)
    return deco


class DFSedge(object):
    """DFSedge class."""

    def __init__(self, frm, to, vevlb):
        """Initialize DFSedge instance."""
        self.frm = frm
        self.to = to
        self.vevlb = vevlb

    def __eq__(self, other):
        """Check equivalence of DFSedge."""
        return (self.frm == other.frm and
                self.to == other.to and
                self.vevlb == other.vevlb)

    def __ne__(self, other):
        """Check if not equal."""
        return not self.__eq__(other)

    def __repr__(self):
        """Represent DFScode in string way."""
        return '(frm={}, to={}, vevlb={})'.format(
            self.frm, self.to, self.vevlb
        )


class DFScode(list):
    """DFScode is a list of DFSedge."""

    def __init__(self):
        """Initialize DFScode."""
        self.rmpath = list()

    def __eq__(self, other):
        """Check equivalence of DFScode."""
        la, lb = len(self), len(other)
        if la != lb:
            return False
        for i in range(la):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        """Check if not equal."""
        return not self.__eq__(other)

    def __repr__(self):
        """Represent DFScode in string way."""
        return ''.join(['[', ','.join(
            [str(dfsedge) for dfsedge in self]), ']']
        )

    def push_back(self, frm, to, vevlb):
        """Update DFScode by adding one edge."""
        self.append(DFSedge(frm, to, vevlb))
        return self

    def to_graph(self, gid=VACANT_GRAPH_ID, is_undirected=True):
        """Construct a graph according to the dfs code."""
        g = Graph(gid,
                  is_undirected=is_undirected,
                  eid_auto_increment=True)
        for dfsedge in self:
            frm, to, (vlb1, elb, vlb2) = dfsedge.frm, dfsedge.to, dfsedge.vevlb
            if vlb1 != VACANT_VERTEX_LABEL:
                g.add_vertex(frm, vlb1)
            if vlb2 != VACANT_VERTEX_LABEL:
                g.add_vertex(to, vlb2)
            g.add_edge(AUTO_EDGE_ID, frm, to, elb)
        return g

    def from_graph(self, g):
        """Build DFScode from graph `g`."""
        raise NotImplementedError('Not inplemented yet.')

    def build_rmpath(self):
        """Build right most path."""
        self.rmpath = list()
        old_frm = None
        for i in range(len(self) - 1, -1, -1):
            dfsedge = self[i]
            frm, to = dfsedge.frm, dfsedge.to
            if frm < to and (old_frm is None or to == old_frm):
                self.rmpath.append(i)
                old_frm = frm
        return self

    def get_num_vertices(self):
        """Return number of vertices in the corresponding graph."""
        return len(set(
            [dfsedge.frm for dfsedge in self] +
            [dfsedge.to for dfsedge in self]
        ))


class PDFS(object):
    """PDFS class."""

    def __init__(self, gid=VACANT_GRAPH_ID, edge=None, prev=None):
        """Initialize PDFS instance."""
        self.gid = gid
        self.edge = edge
        self.prev = prev


class Projected(list):
    """Projected is a list of PDFS.

    Each element of Projected is a projection one frequent graph in one
    original graph.
    """

    def __init__(self):
        """Initialize Projected instance."""
        super(Projected, self).__init__()

    def push_back(self, gid, edge, prev):
        """Update this Projected instance."""
        self.append(PDFS(gid, edge, prev))
        return self


class History(object):
    """History class."""

    def __init__(self, g, pdfs):
        """Initialize History instance."""
        super(History, self).__init__()
        self.edges = list()
        self.vertices_used = collections.defaultdict(int)
        self.edges_used = collections.defaultdict(int)
        if pdfs is None:
            return
        while pdfs:
            e = pdfs.edge
            self.edges.append(e)
            (self.vertices_used[e.frm],
                self.vertices_used[e.to],
                self.edges_used[e.eid]) = 1, 1, 1

            pdfs = pdfs.prev
        self.edges = self.edges[::-1]

    def has_vertex(self, vid):
        """Check if the vertex with vid exists in the history."""
        return self.vertices_used[vid] == 1

    def has_edge(self, eid):
        """Check if the edge with eid exists in the history."""
        return self.edges_used[eid] == 1


class gSpan(object):
    """`gSpan` algorithm."""

    def __init__(self,
                 database_file_name,
                 frequent_stars_folder,
                 output_folder_name,
                 total_instances_file,
                 class_property_file_name,
                 json_folder,
                 min_support=10,
                 min_num_vertices=1,
                 max_num_vertices=float('inf'),
                 max_ngraphs=float('inf'),
                 is_undirected=True,
                 verbose=False,
                 visualize=False,
                 where=False
                ):
        """Initialize gSpan instance."""
        self._database_file_name = database_file_name
        self.frequent_stars_folder = frequent_stars_folder
        self.total_instances_file =total_instances_file
        self.class_property_file_name = class_property_file_name
        self.json_folder = json_folder
        self.graphs = dict()
        self._max_ngraphs = max_ngraphs
        self._is_undirected = is_undirected
        self._min_support = min_support
        self._min_num_vertices = min_num_vertices
        self._max_num_vertices = max_num_vertices
        self._DFScode = DFScode()
        self._support = 0
        self._frequent_size1_subgraphs = list()
        # Include subgraphs with
        # any num(but >= 2, <= max_num_vertices) of vertices.
        self._frequent_subgraphs = list()
        self._counter = itertools.count()
        self._verbose = verbose
        self._visualize = visualize
        self._where = where
        self.timestamps = dict()
        self.poDictionary = dict()
        self.totalInstances = 0
        self.starCounter=itertools.count()
        self.number_of_iterations = 0
        self.number_of_po_iterations = 0
        self.output_folder_name = output_folder_name
        self.starId =0
        file_name_parts = str(self._database_file_name).split('/')
        self.file_name = file_name_parts[len(file_name_parts)-1].split(".")[0]
        print("file name : ", self.file_name)
        #self.subgraph_file_name = open(self.subgraph_folder+'/'+self.file_name, 'w')
        #self.t1 = 0
        #self.t2 = 0
        #self.t3 = 0
        #self.t4 = 0
        self.totalTriples = dict()
        self.newIterations = 0
        self.newIteratedProperties = 0

        if self._max_num_vertices < self._min_num_vertices:
            print('Max number of vertices can not be smaller than '
                  'min number of that.\n'
                  'Set max_num_vertices = min_num_vertices.')
            self._max_num_vertices = self._min_num_vertices
        self._report_df = pd.DataFrame()

    def time_stats(self):
        """Print stats of time."""
        print("Started")
        t1Strat = int(time.time() * 1000.0)
        func_names = ['_read_graphs', 'run']
        time_deltas = collections.defaultdict(float)
        for fn in func_names:
            time_deltas[fn] = round(
                self.timestamps[fn + '_out'] - self.timestamps[fn + '_in'],
                2
            )
        with open(self.class_property_file_name, 'r') as propertyfile:
            self.class_properties = propertyfile.read()
        parts = self.class_properties.split("\t")
        SP = eval(parts[1])
        S = set(SP)
        self.total_properties =len(S)
        fullClassName = parts[0]
        className = parts[0].split("#")[1].strip('>')
        with open(self.total_instances_file, 'r') as instancesfile:
            totalInstances = instancesfile.read()
        insparts = totalInstances.split("\t")
        self.totalInstances=int(insparts[1])
        #poDict = collections.defaultdict(set)
        #self.t1 = (int(time.time() * 1000.0)) - t1Strat
        # time to generate subgraphs by gspan
        #t2Strat = int(time.time() * 1000.0)
        print("Frequent stars identified")
        for g in gList:
            poSet, propSet = g.get_properies_POPairs()
            #print("propSet : ", propSet)
            propSetSorted = sorted(propSet)
            #print("Sorted properties : ", propSetSorted)
            #propStr = str(propSetSorted)
            propStr = str(propSetSorted).strip('[]')
            print("Property string is : ", propStr)
            if propStr in self.poDictionary:
                flag = False
                starlist = self.poDictionary.get(propStr)
                for i in range(len(starlist)):
                    if starlist[i].poSet == poSet:
                        #print("po set matches...")
                        starlist[i].multiplicity = starlist[i].multiplicity + 1
                        self.poDictionary[propStr] = starlist
                        flag = True
                        break
                if not flag:
                    starlist.append(Star(1, poSet))
                    self.poDictionary[propStr] = starlist
                    #print("po set DOES NOT match...")
                #print("key found : ", propStr)
            else:
                #print("key not found : ", propStr)
                starlist = []
                starlist.append(Star(1, poSet))
                self.poDictionary[propStr] = starlist
        #self.t2 = (int(time.time() * 1000.0)) - t2Strat
        # time taken to create poDictionary for subgraphs and property sets
        #minStars = 9999999
        #diff = 9999999
        bestStarList = []
        bestPropertyList = []

        #t3Strat = int(time.time() * 1000.0)
        ttriples = 99999999

        for key in sorted(self.poDictionary.keys()):
            triples = 0
            starlist = self.poDictionary[key]
            for l in starlist:
                triples = triples + l.multiplicity + len(l.poSet) + l.multiplicity*(self.total_properties-len(l.poSet))
            self.totalTriples[key] = triples
        for key in self.totalTriples:
            print("properties and triples: ", key,self.totalTriples[key])
        for key in sorted(self.poDictionary.keys()):
            print("Key : ", key)
            self.number_of_iterations = self.number_of_iterations + 1
            starlist = self.poDictionary[key]
            self.newIterations = self.newIterations + len(starlist)
            proplist = key.split(',')
            multiplicity = 0

            for l in starlist:
                self.number_of_po_iterations = self.number_of_po_iterations + 1
                multiplicity = multiplicity + l.multiplicity
            if len(proplist) >= 2 and self.totalTriples[key] < ttriples:
                #diff = diff2
                minStars = len(starlist)
                bestStarList = starlist
                bestPropertyList = proplist
                ttriples= self.totalTriples[key]
        print("Best property set : ", bestPropertyList)
        #self.t3 = (int(time.time() * 1000.0)) - t3Strat
        frequent_stars_file = open(self.frequent_stars_folder+'/'+self.file_name+"efsp", 'w')
        #t4Strat = int(time.time() * 1000.0)
        for s in bestStarList:
            print("Printing at the end", len(bestStarList))
            print("multiplicity : ", s.multiplicity)
            support = int(s.multiplicity)
            self.starId = next(self.starCounter)
            vertex_counter = itertools.count()
            edge_cunter = itertools.count()
            print("Support is : ", support)
            if support >= self._min_support:
                print("new star graph pattern")
                surrogateId = next(vertex_counter)
                surrogatelbl = "?x" + str(self.starId)
                g = Graph(self.starId,  is_undirected=False)
                g.add_vertex(surrogateId, surrogatelbl)
                #print("subject : ", subId, sublbl)
                self._frequent_size1_subgraphs.append(g)
                for po in s.poSet:
                    #vID = next(self.starCounter)
                    to_vertex_ID = next(vertex_counter)
                    g.add_vertex(to_vertex_ID, po[1])
                    #print("to vertex : ", vID, po[1])
                    eid = next(edge_cunter)
                    #print("edge details : ", eid, surrogateId, to_vertex_ID, po[0])
                    g.add_edge(eid, surrogateId, to_vertex_ID, po[0])
                    if len(s.poSet) <= 1:
                        print("starList has no elements")
                        self._report_size1(g, support=s.multiplicity)
                frequent_stars_file.write("%s" % g.display())
                frequent_stars_file.write("\n")
                #g.display()
                print('\nSupport: {}'.format(support))
                print('\n-----------------\n')
        # time take to write the frequent stars
        frequent_stars_file.flush()
        frequent_stars_file.close()
        S1 = set()
        for i in bestPropertyList:
            S1.add("<"+i.strip('\'').strip(' \'')+">")
        attDict = {}
        attDict["class"] = fullClassName
        attDict["factorizedAttributesOutdegree"] = list(S1)
        attDict["factorizedAttributesIndegree"] = []
        attDict["nonfactorizedAttributesOutdegree"] = list(S-S1)
        attDict["nonfactorizedAttributesIndegree"] = []
        classDict = {}
        classDict[fullClassName] = attDict
        print(classDict)
        # f = open(self.json_folder + "/" + self.className, "w")
        with open(self.json_folder + "/" + className, 'w') as f:
            f.write(json.dumps(classDict, ensure_ascii=False))
            f.flush()
            f.close()

        if not os.path.exists(self.output_folder_name+'/efspResult'):
            result_file = open(self.output_folder_name+'/efspResult', 'w+')
            result_file.write("%s\t%s\t%s\t%s\t%s" % ('Approach','Class','Exe.Time(ms)','PropertySetIterations','#FrequentStars'))
            result_file.write("\n")
        else:
            result_file = open(self.output_folder_name + '/efspResult', 'a+')
        result_file.write("%s\t%s\t%s\t%s\t%s" % ('EFSP',self.file_name, format(time_deltas['run']),self.number_of_iterations,self.starId))
        result_file.write("\n")
        result_file.flush()
        result_file.close()
        print(bestPropertyList)
        return self


    @record_timestamp
    def _read_graphs(self):
        self.graphs = dict()
        with codecs.open(self._database_file_name, 'r', 'utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
            tgraph, graph_cnt = None, 0
            for i, line in enumerate(lines):
                cols = line.split(' ')
                if cols[0] == 't':
                    if tgraph is not None:
                        self.graphs[graph_cnt] = tgraph
                        graph_cnt += 1
                        tgraph = None
                    if cols[-1] == '-1' or graph_cnt >= self._max_ngraphs:
                        break
                    tgraph = Graph(graph_cnt,
                                   is_undirected=self._is_undirected,
                                   eid_auto_increment=True)
                elif cols[0] == 'v':
                    tgraph.add_vertex(cols[1], cols[2])
                elif cols[0] == 'e':
                    tgraph.add_edge(AUTO_EDGE_ID, cols[1], cols[2], cols[3])
            # adapt to input files that do not end with 't # -1'
            if tgraph is not None:
                self.graphs[graph_cnt] = tgraph
        return self

    @record_timestamp
    def _generate_1edge_frequent_subgraphs(self):
        vlb_counter = collections.Counter()
        vevlb_counter = collections.Counter()
        vlb_counted = set()
        vevlb_counted = set()
        for g in self.graphs.values():
            for v in g.vertices.values():
                if (g.gid, v.vlb) not in vlb_counted:
                    vlb_counter[v.vlb] += 1
                vlb_counted.add((g.gid, v.vlb))
                for to, e in v.edges.items():
                    vlb1, vlb2 = v.vlb, g.vertices[to].vlb
                    if self._is_undirected and vlb1 > vlb2:
                        vlb1, vlb2 = vlb2, vlb1
                    if (g.gid, (vlb1, e.elb, vlb2)) not in vevlb_counter:
                        vevlb_counter[(vlb1, e.elb, vlb2)] += 1
                    vevlb_counted.add((g.gid, (vlb1, e.elb, vlb2)))
        # add frequent vertices.
        for vlb, cnt in vlb_counter.items():
            if cnt >= self._min_support:
                g = Graph(gid=next(self._counter),
                          is_undirected=self._is_undirected)
                g.add_vertex(0, vlb)
                self._frequent_size1_subgraphs.append(g)
                if self._min_num_vertices <= 1:
                    self._report_size1(g, support=cnt)
            else:
                continue
        if self._min_num_vertices > 1:
            self._counter = itertools.count()

    @record_timestamp
    def run(self):
        """Run the gSpan algorithm."""
        self._read_graphs()
        self._generate_1edge_frequent_subgraphs()
        if self._max_num_vertices < 2:
            return
        root = collections.defaultdict(Projected)
        for gid, g in self.graphs.items():
            for vid, v in g.vertices.items():
                edges = self._get_forward_root_edges(g, vid)
                for e in edges:
                    root[(v.vlb, e.elb, g.vertices[e.to].vlb)].append(
                        PDFS(gid, e, None)
                    )

        for vevlb, projected in root.items():
            self._DFScode.append(DFSedge(0, 1, vevlb))
            self._subgraph_mining(projected)
            self._DFScode.pop()

    def _get_support(self, projected):
        return len(set([pdfs.gid for pdfs in projected]))

    def _report_size1(self, g, support):
        g.display()
        print('\nSupport: {}'.format(support))
        print('\n-----------------\n')

    def _report(self, projected):
        self._frequent_subgraphs.append(copy.copy(self._DFScode))
        if self._DFScode.get_num_vertices() < self._min_num_vertices:
            return
        g = self._DFScode.to_graph(gid=next(self._counter),
                                   is_undirected=self._is_undirected)
        display_str = g.display()
        print('\nSupport is: {}'.format(self._support))
        gList.append(g)
        self._report_df = self._report_df.append(
            pd.DataFrame(
                {
                    'support': [self._support],
                    'description': [display_str],
                    'num_vert': self._DFScode.get_num_vertices()
                },
                index=[int(repr(self._counter)[6:-1])]
            )
        )
        if self._visualize:
            g.plot()
        if self._where:
            print('where: {}'.format(list(set([p.gid for p in projected]))))
        print('\n-----------------\n')

    def _get_forward_root_edges(self, g, frm):
        result = []
        v_frm = g.vertices[frm]
        for to, e in v_frm.edges.items():
            if (not self._is_undirected) or v_frm.vlb <= g.vertices[to].vlb:
                result.append(e)
        return result

    def _get_backward_edge(self, g, e1, e2, history):
        if self._is_undirected and e1 == e2:
            return None
        for to, e in g.vertices[e2.to].edges.items():
            if history.has_edge(e.eid) or e.to != e1.frm:
                continue
            # if reture here, then self._DFScodep[0] != dfs_code_min[0]
            # should be checked in _is_min(). or:
            if self._is_undirected:
                if e1.elb < e.elb or (
                        e1.elb == e.elb and
                        g.vertices[e1.to].vlb <= g.vertices[e2.to].vlb):
                    return e
            else:
                #print(g.vertices[e1.frm].vlb, "-----",g.vertices[e2.to])
                #if g.vertices[e1.frm].vlb < g.vertices[e2.to] or (
                #        g.vertices[e1.frm].vlb == g.vertices[e2.to] and
                 #       e1.elb <= e.elb):
                if g.vertices[e1.frm].vlb < g.vertices[e2.to].vlb or (
                            g.vertices[e1.frm].vlb == g.vertices[e2.to].vlb and
                            e1.elb <= e.elb):
                    return e
            # if e1.elb < e.elb or (e1.elb == e.elb and
            #     g.vertices[e1.to].vlb <= g.vertices[e2.to].vlb):
            #     return e
        return None

    def _get_forward_pure_edges(self, g, rm_edge, min_vlb, history):
        result = []
        for to, e in g.vertices[rm_edge.to].edges.items():
            if min_vlb <= g.vertices[e.to].vlb and (
                    not history.has_vertex(e.to)):
                result.append(e)
        return result

    def _get_forward_rmpath_edges(self, g, rm_edge, min_vlb, history):
        result = []
        to_vlb = g.vertices[rm_edge.to].vlb
        for to, e in g.vertices[rm_edge.frm].edges.items():
            new_to_vlb = g.vertices[to].vlb
            if (rm_edge.to == e.to or
                    min_vlb > new_to_vlb or
                    history.has_vertex(e.to)):
                continue
            if rm_edge.elb < e.elb or (rm_edge.elb == e.elb and
                                       to_vlb <= new_to_vlb):
                result.append(e)
        return result

    def _is_min(self):
        if self._verbose:
            print('is_min: checking {}'.format(self._DFScode))
        if len(self._DFScode) == 1:
            return True
        g = self._DFScode.to_graph(gid=VACANT_GRAPH_ID,
                                   is_undirected=self._is_undirected)
        dfs_code_min = DFScode()
        root = collections.defaultdict(Projected)
        for vid, v in g.vertices.items():
            edges = self._get_forward_root_edges(g, vid)
            for e in edges:
                root[(v.vlb, e.elb, g.vertices[e.to].vlb)].append(
                    PDFS(g.gid, e, None))
        min_vevlb = min(root.keys())
        dfs_code_min.append(DFSedge(0, 1, min_vevlb))
        # No need to check if is min code because of pruning in get_*_edge*.

        def project_is_min(projected):
            dfs_code_min.build_rmpath()
            rmpath = dfs_code_min.rmpath
            min_vlb = dfs_code_min[0].vevlb[0]
            maxtoc = dfs_code_min[rmpath[0]].to

            backward_root = collections.defaultdict(Projected)
            flag, newto = False, 0,
            end = 0 if self._is_undirected else -1
            for i in range(len(rmpath) - 1, end, -1):
                if flag:
                    break
                for p in projected:
                    history = History(g, p)
                    e = self._get_backward_edge(g,
                                                history.edges[rmpath[i]],
                                                history.edges[rmpath[0]],
                                                history)
                    if e is not None:
                        backward_root[e.elb].append(PDFS(g.gid, e, p))
                        newto = dfs_code_min[rmpath[i]].frm
                        flag = True
            if flag:
                backward_min_elb = min(backward_root.keys())
                dfs_code_min.append(DFSedge(
                    maxtoc, newto,
                    (VACANT_VERTEX_LABEL,
                     backward_min_elb,
                     VACANT_VERTEX_LABEL)
                ))
                idx = len(dfs_code_min) - 1
                if self._DFScode[idx] != dfs_code_min[idx]:
                    return False
                return project_is_min(backward_root[backward_min_elb])

            forward_root = collections.defaultdict(Projected)
            flag, newfrm = False, 0
            for p in projected:
                history = History(g, p)
                edges = self._get_forward_pure_edges(g,
                                                     history.edges[rmpath[0]],
                                                     min_vlb,
                                                     history)
                if len(edges) > 0:
                    flag = True
                    newfrm = maxtoc
                    for e in edges:
                        forward_root[
                            (e.elb, g.vertices[e.to].vlb)
                        ].append(PDFS(g.gid, e, p))
            for rmpath_i in rmpath:
                if flag:
                    break
                for p in projected:
                    history = History(g, p)
                    edges = self._get_forward_rmpath_edges(g,
                                                           history.edges[
                                                               rmpath_i],
                                                           min_vlb,
                                                           history)
                    if len(edges) > 0:
                        flag = True
                        newfrm = dfs_code_min[rmpath_i].frm
                        for e in edges:
                            forward_root[
                                (e.elb, g.vertices[e.to].vlb)
                            ].append(PDFS(g.gid, e, p))

            if not flag:
                return True

            forward_min_evlb = min(forward_root.keys())
            dfs_code_min.append(DFSedge(
                newfrm, maxtoc + 1,
                (VACANT_VERTEX_LABEL, forward_min_evlb[0], forward_min_evlb[1]))
            )
            idx = len(dfs_code_min) - 1
            if self._DFScode[idx] != dfs_code_min[idx]:
                return False
            return project_is_min(forward_root[forward_min_evlb])

        res = project_is_min(root[min_vevlb])
        return res

    def _subgraph_mining(self, projected):
        self._support = self._get_support(projected)
        if self._support < self._min_support:
            return
        if not self._is_min():
            return
        self._report(projected)

        num_vertices = self._DFScode.get_num_vertices()
        self._DFScode.build_rmpath()
        rmpath = self._DFScode.rmpath
        maxtoc = self._DFScode[rmpath[0]].to
        min_vlb = self._DFScode[0].vevlb[0]

        forward_root = collections.defaultdict(Projected)
        backward_root = collections.defaultdict(Projected)
        for p in projected:
            g = self.graphs[p.gid]
            history = History(g, p)
            # backward
            for rmpath_i in rmpath[::-1]:
                e = self._get_backward_edge(g,
                                            history.edges[rmpath_i],
                                            history.edges[rmpath[0]],
                                            history)
                if e is not None:
                    backward_root[
                        (self._DFScode[rmpath_i].frm, e.elb)
                    ].append(PDFS(g.gid, e, p))
            # pure forward
            if num_vertices >= self._max_num_vertices:
                continue
            edges = self._get_forward_pure_edges(g,
                                                 history.edges[rmpath[0]],
                                                 min_vlb,
                                                 history)
            for e in edges:
                forward_root[
                    (maxtoc, e.elb, g.vertices[e.to].vlb)
                ].append(PDFS(g.gid, e, p))
            # rmpath forward
            for rmpath_i in rmpath:
                edges = self._get_forward_rmpath_edges(g,
                                                       history.edges[rmpath_i],
                                                       min_vlb,
                                                       history)
                for e in edges:
                    forward_root[
                        (self._DFScode[rmpath_i].frm,
                         e.elb, g.vertices[e.to].vlb)
                    ].append(PDFS(g.gid, e, p))

        # backward
        for to, elb in backward_root:
            self._DFScode.append(DFSedge(
                maxtoc, to,
                (VACANT_VERTEX_LABEL, elb, VACANT_VERTEX_LABEL))
            )
            self._subgraph_mining(backward_root[(to, elb)])
            self._DFScode.pop()
        # forward
        # No need to check if num_vertices >= self._max_num_vertices.
        # Because forward_root has no element.
        for frm, elb, vlb2 in forward_root:
            self._DFScode.append(DFSedge(
                frm, maxtoc + 1,
                (VACANT_VERTEX_LABEL, elb, vlb2))
            )
            self._subgraph_mining(forward_root[(frm, elb, vlb2)])
            self._DFScode.pop()

        return self

class Star:
    def __init__(self, multiplicity, poSet):
        self.poSet = poSet
        self.multiplicity = int(multiplicity)