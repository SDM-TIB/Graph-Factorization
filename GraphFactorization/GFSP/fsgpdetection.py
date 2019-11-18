import collections
import os

import itertools

import pandas as pd
import time
import json
from graph import Graph
from itertools import combinations

def record_timestamp(func):
    """Record timestamp before and after call of `func`."""
    def deco(self):
        """self.timestamps[func.__name__ + '_in'] = time.time()"""
        self.timestamps[func.__name__ + '_in'] = int(time.time() * 1000.0)
        func(self)
        # self.timestamps[func.__name__ + '_out'] = time.time()
        self.timestamps[func.__name__ + '_out'] = int(time.time() * 1000.0)
    return deco

class fgpDetection(object):
    """`fgpDetection` algorithm."""

    def __init__(self,
                 list_file_name,
                 class_property_file_name,
                 frequent_stars_folder,
                 output_folder_name,
                 instances_file,
                 json_folder,
                 min_support=1,
                 ):
        """Initialize gSpan instance."""
        self.list_file_name = list_file_name
        self.frequent_stars_folder = frequent_stars_folder
        self.output_folder_name = output_folder_name
        self.json_folder = json_folder
        self.graphs = dict()
        self._min_support = min_support
        self._support = 0
        self._frequent_size1_subgraphs = list()
        self._frequent_subgraphs = list()
        self._counter = itertools.count()
        self.timestamps = dict()
        self.instances_file = instances_file
        self._report_df = pd.DataFrame()
        self.starCounter = itertools.count()
        self.edgeCounter = itertools.count()
        self.AM = 0
        self.class_property_file_name = class_property_file_name
        self.number_of_iterations = 0
        self.number_of_po_iterations = 0
        self.number_of_iterationsNew = 1
        self.number_of_po_iterationsNew = 0
        self.starId = 0
        self.className=''

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

        if not os.path.exists(self.output_folder_name+'/gfspResult'):
            result_file = open(self.output_folder_name+'/gfspResult', 'w+')
            result_file.write("%s\t%s\t%s\t%s\t%s" % ('Approach','Class','Exe.Time(ms)','PropertySetIterations','#FrequentStars'))
            result_file.write("\n")
        else:
            result_file = open(self.output_folder_name + '/gfspResult', 'a+')
        result_file.write("%s\t%s\t%s\t%s\t%s" % ('GFSP',self.className, format(time_deltas['run']),self.number_of_iterations+1,self.starId+1))
        result_file.write("\n")
        result_file.flush()
        result_file.close()

        return self



    @record_timestamp
    def run(self):
        #improved removal of inverse functional properties
        #improved iterating lattice

        starDictionary = {}
        with open(self.class_property_file_name, 'r') as propertyfile:
            self.class_properties = propertyfile.read()
        parts = self.class_properties.split("\t")
        SP = eval(parts[1])
        S = set(SP)
        fullClassName = parts[0]
        self.className = parts[0].split('#')[1]
        self.className = self.className.replace('<', '').replace('>', '')
        #poIteration_file = open(self.output_folder_name + '/' + self.className, 'w+')

        with open(self.instances_file, 'r') as instancesfile:
            instances = instancesfile.read()
        instancesParts = instances.split("\t")
        self.AM = int(instancesParts[1])
        print("Total instances : ", self.AM)
        with open(self.list_file_name) as f:
            for line in f:
                linePart = line.split("\t")
                starDictionary[linePart[1]] = linePart[0]
        AMI = len(starDictionary)
        #print("List of properties before removing : ", SP)
        if self.AM == AMI:
            start_time = time.time() * 1000.0
            for p in SP:
                poPairsSet = set()
                for k,v in starDictionary.items():  # iterate over the list
                    kparts = k.split("&&")
                    for poPair in kparts:  # iterate over the po pairs in each list element
                        if p in poPair:
                            poPairsSet.add(poPair)
                if len(poPairsSet) == self.AM:
                    SP.remove(p)
            end_time = time.time() * 1000.0
            print("--- %s milli seconds taken to remove functional and inverse functional attributes ---" % (end_time - start_time))

        frequent_stars_file = open(self.frequent_stars_folder+'/'+self.className+"gfsp", 'w+')
        SP1 = set()
        starDictionaryNew1 = {}
        while True:
            print("while started")

            AMI = len(starDictionary)
            if self.number_of_po_iterationsNew == 0:
                self.number_of_po_iterationsNew = AMI
            print("length of dictionary : ", AMI)
            SP2 = SP.copy()
            if len(SP) >= 2:
                if AMI == 1:
                    print("First part working")
                    self.number_of_iterations = self.number_of_iterations + 1
                    #poIteration_file.write("%s\t%s" % (SP, 'start'))
                    #poIteration_file.write("\n")
                    #poIteration_file.write("\n")
                    self.number_of_po_iterations = self.number_of_po_iterations +1
                    #print("Iteration with properties 0 : ", SP)
                    print("Printing at the start")
                    self.starId = next(self.starCounter)
                    for k, v in starDictionary.items():
                        if int(v) >= self._min_support:
                            g = Graph(self.starId, is_undirected=False)
                            g.add_vertex(0, "?x" + str(self.starId))
                            self._frequent_size1_subgraphs.append(g)
                            poSet = k.split("&&")
                            for po in poSet:
                                poParts = po.split(",")
                                vID = next(self.starCounter)
                                g.add_vertex(vID, po[1])
                                g.add_edge(next(self.edgeCounter), self.starId, vID, poParts[0])
                                if len(k) <= 1:
                                    print("starList has no elements")
                                    self._report_size1(g, support=int(v))
                            g.display()
                            frequent_stars_file.write("%s" % g.display())
                            frequent_stars_file.write("\n")
                            print('\nSupport: {}'.format(int(v)))
                    frequent_stars_file.flush()
                    frequent_stars_file.close()
                    print("Best set of properties in start : ", SP2)
                    attDict = {}
                    attDict["class"] = fullClassName
                    attDict["factorizedAttributesOutdegree"] = list(SP2)
                    attDict["factorizedAttributesIndegree"] =[]
                    attDict["nonfactorizedAttributesOutdegree"] = list(S.difference(SP2))
                    attDict["nonfactorizedAttributesIndegree"] = []
                    classDict = {}
                    classDict[fullClassName] = attDict
                    print(classDict)
                    with open(self.json_folder + "/" + self.className, 'w') as f:
                        f.write(json.dumps(classDict, ensure_ascii=False))
                        #f.write(str(classDict))
                        f.flush()
                        f.close()
                    print("Returning SP2")
                    return SP2
                else:
                    print("Second part working : ", SP)
                    fValue1 = fValue = self.computeValue(AMI, SP)
                    #self.number_of_iterations = self.number_of_iterations + 1
                    #poIteration_file.write("%s\t%s" % (SP,'mid'))
                    #poIteration_file.write("\n")
                    self.number_of_po_iterations = self.number_of_po_iterations + 1
                for k, v in starDictionary.items():
                    poSet = k.split("&&")
                    #print("Iterating for : ", poSet)
                    break
                for po in poSet:
                    poParts = po.split(",")
                    print("Attribute is : ", poParts[0])
                    #print("SP is now : ", SP)
                    if poParts[0] in SP:
                        SP2 = SP.copy()
                        SP2.remove(poParts[0])
                        starDictionaryNew = {}
                        if len(SP2) >= 2:
                            self.number_of_iterationsNew = self.number_of_iterationsNew + 1
                            for k, v in starDictionary.items():
                                self.number_of_po_iterations = self.number_of_po_iterations + 1
                                pos = k.split("&&")
                                kstr = ""
                                for pair in pos:
                                    pairParts = pair.split(",")
                                    if poParts[0] not in pair and pairParts[0] in SP:
                                        #print("Attribute is not in pair : ", poParts[0], pair)
                                        if kstr:
                                           kstr = kstr + "&&"
                                        kstr = kstr + pair
                                if kstr in starDictionaryNew:
                                    starDictionaryNew[kstr] = int(starDictionaryNew[kstr]) + int(starDictionary[k])
                                else:
                                    starDictionaryNew[kstr] = starDictionary[k]
                            AMI = len(starDictionaryNew)
                            self.number_of_po_iterationsNew = self.number_of_po_iterationsNew + AMI
                            value = self.computeValue(AMI, SP2)
                            print("value at 1 is : ", value, SP2)
                            self.number_of_iterations = self.number_of_iterations + 1
                            #poIteration_file.write("%s\t%s" % (SP2, 'end'))
                            #poIteration_file.write("\n")
                            if AMI == 1 and value > fValue1:
                                print("Printing in the middle")
                                SP1 = SP2.copy()
                                #poIteration_file.write("%s\t%s" % (SP1, 'best set mid'))
                                #poIteration_file.write("\n")
                                self.starId = next(self.starCounter)
                                for k, v in starDictionaryNew.items():
                                    if int(v) >= self._min_support:
                                        g = Graph(self.starId, is_undirected=False)
                                        g.add_vertex(0, "?x" + str(self.starId))
                                        self._frequent_size1_subgraphs.append(g)
                                        poSet = k.split("&&")
                                        for po in poSet:
                                            poParts = po.split(",")
                                            vID = next(self.starCounter)
                                            g.add_vertex(vID, poParts[1])
                                            g.add_edge(next(self.edgeCounter), self.starId, vID, poParts[0])
                                            if len(k) <= 1:
                                                self._report_size1(g, support=int(v))
                                        frequent_stars_file.write("%s" % g.display())
                                        frequent_stars_file.write("\n")
                                        g.display()
                                frequent_stars_file.flush()
                                frequent_stars_file.close()
                                        #print("Best set of properties in middle : ", SP1)
                                print("exiting one ")
                                attDict = {}
                                attDict["class"] = fullClassName
                                attDict["factorizedAttributesOutdegree"] = list(SP1)
                                attDict["factorizedAttributesIndegree"] = []
                                attDict["nonfactorizedAttributesOutdegree"] = list(S.difference(SP1))
                                attDict["nonfactorizedAttributesIndegree"] = []
                                classDict = {}
                                classDict[fullClassName] = attDict
                                print(classDict)
                                #f = open(self.json_folder + "/" + self.className, "w")
                                #f.write(str(classDict))
                                with open(self.json_folder + "/" + self.className, 'w') as f:
                                    f.write(json.dumps(classDict, ensure_ascii=False))
                                    f.flush()
                                    f.close()
                                print("Returning SP1")
                                return SP1
                            if value > fValue1:
                                print("value > fvalue1 : ", value, fValue1)
                                fValue1 = value
                                #print("changed SP1 and SP2: ", SP1, SP2)
                                SP1 = SP2.copy()
                                #poIteration_file.write("%s\t%s" % (SP1, 'best set end'))
                                #poIteration_file.write("\n")
                                #print("SP1 after assignment : ", SP1)
                                starDictionaryNew1 = starDictionaryNew
                                #print("new dictionary found in starNewDictionary 1")
                            else:
                                starDictionaryNew1 = starDictionary
                                print("New dictionary found")
                        elif fValue >= 0:
                            starDictionaryNew1 = starDictionary
                            print("new dictionary found in starNewDictionary 1 level 2")
                            break
                print("fvalue : ", SP,fValue, fValue1)
                if SP1:
                    SP = SP1
                starDictionary = starDictionaryNew1
            if fValue1 <= fValue:
                break


        for k,v in starDictionary.items():
            self.starId = next(self.starCounter)
            vertex_counter = itertools.count()
            edge_cunter = itertools.count()
            if int(v) >= self._min_support:
                surrogateId = next(vertex_counter)
                surrogatelbl = "?x" + str(self.starId)
                g = Graph(self.starId, is_undirected=False)
                g.add_vertex(surrogateId, surrogatelbl)
                self._frequent_size1_subgraphs.append(g)
                pos = k.split("&&")
                for pair in pos:
                    pairParts = pair.split(",")
                    to_vertex_ID = next(vertex_counter)
                    g.add_vertex(to_vertex_ID, pairParts[1])
                    eid = next(edge_cunter)
                    g.add_edge(eid, surrogateId, to_vertex_ID, pairParts[0])
                    if len(k) <= 1:
                        print("starList has no elements")
                        self._report_size1(g, support=v)
                frequent_stars_file.write("%s" % g.display())
                frequent_stars_file.write("\n")
                #g.display()
                print('\nSupport: {}'.format(v))
                print('\n-----------------\n')
        print("Total number of iterations : ", self.number_of_iterations)
        print("Total number of po iterations ", self.number_of_po_iterations)
        frequent_stars_file.flush()
        frequent_stars_file.close()
        #print("Best property set at the end is: ", SP1)
        attDict = {}
        attDict["class"] = fullClassName
        attDict["factorizedAttributesOutdegree"] = list(SP)
        attDict["factorizedAttributesIndegree"] = []
        attDict["nonfactorizedAttributesOutdegree"] = list(S.difference(SP))
        attDict["nonfactorizedAttributesIndegree"] = []
        classDict = {}
        classDict[fullClassName] = attDict
        with open(self.json_folder + "/" + self.className, 'w') as f:
            f.write(json.dumps(classDict, ensure_ascii=False))
            f.flush()
            f.close()

    def computeValue(self, AMI, SP):
        return ((self.AM * (len(SP) - 1)) / (len(SP) + 1)) - AMI


    def _report_size1(self, g, support):
        g.display()
        print('\nSupport: {}'.format(support))
        print('\n-----------------\n')