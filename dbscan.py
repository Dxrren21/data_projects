#Clustering program based on the DBSCAN Algorithm 

import sys 
import math


filename = str(sys.argv[1])
n_clusters = int(sys.argv[2])
Eps = float(sys.argv[3])
MinPts = int(sys.argv[4])

path_to_input_file = f'./{filename}' #input assumed to be in the same directory as file 

database = []

class data_point:
    def __init__(self, id, x, y, cluster): 
        self.id = int(id) 
        self.x = float(x) 
        self.y = float(y) 
        self.cluster = None  
        self.cluster_obj = None

    def distance(self, data2): 
        point1 = (self.x, self.y)
        point2 = (data2.x, data2.y)
        distance = math.dist(point1, point2)
        return distance

    def print(self): 
        print(str(self.id) + " " + str(self.x) + " " + str(self.y) + " " + str(self.cluster))
    
    def set_cluster(self, cluster): 
        if (cluster == "noise"): 
            self.cluster = "noise"
        else: 
            self.cluster = cluster.id
            self.cluster_obj = cluster

    def write_cluster(self): 
        if (self.cluster == "noise"):
            return
        with open(self.cluster_obj.filename, "a") as file: 
            file.write(str(self.id) + "\n")


class cluster_label: 
    next_id = 0

    def __init__(self):
        self.id = cluster_label.next_id
        cluster_label.next_id += 1 
        self.filename = filename[0:-4] + "_cluster_" + str(self.id) + ".txt"


def get_seed(list_neighbours, og_datapt): 
    new_seed = list(list_neighbours)
    for element in new_seed: 
        if element.id == og_datapt.id: 
            new_seed.remove(element)
    return new_seed 

def get_neighbours(centroid): 
    c_neighbours = []
    for data_point in database: 
        distance = float(centroid.distance(data_point))
        if (distance <= Eps): 
            c_neighbours.append(data_point)
    return c_neighbours

# given two lists attach 1st then 2nd without any duplicates

def list_combine(list1, list2): 
    for element in list2: 
        if element not in list1: 
            list1.append(element)

# given a list of neighbours, find the majority cluster
def majority(neighbours): 
    if not neighbours:
        return None  
    
    clust = {}
    for neigh in neighbours: 
        clust[neigh.cluster_obj] = clust.get(neigh.cluster_obj, 0) + 1
    

    if clust:
        return max(clust, key=clust.get)
    else:
        return None

    

with open(path_to_input_file, "r") as input_file: 
    for line in input_file: 
        line = line.strip()
        data = line.split()
        database.append(data_point(data[0], float(data[1]), float(data[2]), None))

for p in database:
 
    if p.cluster is not None: 
        continue 
    
    neighbours = get_neighbours(p)

    if len(neighbours) < int(MinPts): 
        p.set_cluster("noise")
        continue 
    # create new cluster label 
    
    cluster_id = cluster_label() #returns object of cluster label


    # edge case 

    if cluster_id.id >= n_clusters: 
        cluster_id = majority(neighbours)
        if cluster_id is None: 
            p.set_cluster("noise")
            continue

    p.set_cluster(cluster_id)

    
    seed = get_seed(neighbours, p)
    
    for q in seed:        
        if q.cluster == "noise": 
            q.set_cluster(cluster_id)

        if q.cluster is not None: 
            continue
        
        q_neighbours = get_neighbours(q) 

        q.set_cluster(cluster_id)

        if len(q_neighbours) < MinPts: 
            continue
        else: 
            for element in q_neighbours: 
                if (element not in seed) & (element != p) & (element != q):
                    seed.append(element)


for data in database: 
    data.write_cluster()
