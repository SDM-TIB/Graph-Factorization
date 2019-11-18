import collections
import os

import time
from SPARQLWrapper import SPARQLWrapper, JSON

def record_timestamp(func):
    """Record timestamp before and after call of `func`."""

    def deco(self):
        """self.timestamps[func.__name__ + '_in'] = time.time()"""
        self.timestamps[func.__name__ + '_in'] = int(time.time() * 1000.0)
        func(self)
        # self.timestamps[func.__name__ + '_out'] = time.time()
        self.timestamps[func.__name__ + '_out'] = int(time.time() * 1000.0)
    return deco

class collectStars(object):
    def __init__(self,
                 endpoint_url,
                 class_property_file_name,
                 starList_folder_name,
                 instances_folder,
                 result_folder
                 ):
        """Initialize instance."""
        self.class_property_file_name = class_property_file_name
        self.starList_folder_name = starList_folder_name
        self.instances_folder = instances_folder
        self.result_folder = result_folder
        self.timestamps = dict()
        self.endpoint_url = endpoint_url
        self.class_properties = ""
        self.query_str = ""
        self.pList = []
        self.oList = []
        self._limit = 1000000
        self._offset = 0
        self.className = ""

    def time_stats(self):
        """Print stats of time."""
        func_names = ['run']
        time_deltas = collections.defaultdict(float)
        for fn in func_names:
            time_deltas[fn] = round(self.timestamps[fn + '_out'] - self.timestamps[fn + '_in'],2)
        print('Total:\t{} ms'.format(time_deltas['run']))
        if not os.path.exists(self.result_folder+'/groupByResult'):
            result_file = open(self.result_folder+'/groupByResult', 'a+')
            result_file.write("%s\t%s\t%s" % ('Approach','Class','Exe.Time(ms)'))
            result_file.write("\n")
        else:
            result_file = open(self.result_folder + '/groupByResult', 'a+')
        result_file.write("%s\t%s\t%s" % ('rdf2Graph',self.className, format(time_deltas['run'])))
        result_file.write("\n")
        result_file.flush()
        result_file.close()
        return self


    @record_timestamp
    def run(self):
        # Read class and properties
        with open(self.class_property_file_name, 'r') as propertyfile:
            self.class_properties = propertyfile.read()
        self.built_query()
        q = self.query_str + " OFFSET " + str(self._offset) + " LIMIT " + str(self._limit)
        print("query with limit is : ",q)
        data = self.runQuery(q)
        total_instances = 0
        list_file = open(self.starList_folder_name+"/"+self.className, 'w+')
        while len(data["results"]["bindings"])>0:
            self._offset = self._offset + self._limit
            for res in data["results"]["bindings"]:
                poStr = ""
                total_instances = total_instances + int(res["instances"]["value"])
                for i in range(len(self.pList)):
                    poStr = poStr +self.pList[i]+","+res[self.oList[i][1:]]["value"]+"&&"
                poStr = poStr[:len(poStr)-1]
                list_file.write("%s\t%s"%(res["instances"]["value"],poStr))
                list_file.write("\n")
            q = self.query_str + " OFFSET " + str(self._offset) + " LIMIT " + str(self._limit)
            #print("query with limit is : ", q)
            data = self.runQuery(q)
        list_file.flush()
        list_file.close()
        #print("dictionary size : ", int(len(measDictionary)))
        print("Total Instances : ", total_instances)
        instances_file = open(self.instances_folder + "/" + self.className, 'w')
        instances_file.write("%s\t%s" % ("totalInstances", total_instances))
        instances_file.write("\n")
        instances_file.flush()
        instances_file.close()


    def built_query(self):
        print("Class properties are : ", self.class_properties)
        strPart = self.class_properties.split("\t")
        print("Class : ", strPart[0])
        print("Properties : ", strPart[1])
        classparts = strPart[0].split('#')
        self.className= classparts[1].replace('<', '').replace('>', '')
        pSet = eval(strPart[1])
        i = 1
        select = "(COUNT(DISTINCT ?s) AS ?instances)"
        groupBy = ""
        where = ""
        for p in pSet:
            self.pList.append(p)
            o = "?o"+str(i)
            self.oList.append(o)
            i=i+1
            select = select + " " + o
            groupBy = groupBy + " " + o
            where = where + " ?s " + p + " " + o + "." + "\n"
        self.query_str = "SELECT " + select + " \nWHERE { " + where + " } " + " \nGROUP BY " + groupBy


    def runQuery(self, q):
        sparql = SPARQLWrapper(self.endpoint_url.strip())
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results