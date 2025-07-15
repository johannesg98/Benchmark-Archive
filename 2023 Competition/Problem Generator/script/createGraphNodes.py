import argparse
import os
import logging
import sys

#self.get_loc_id(x,y,rows,cols)

class GraphCreator:
    def __init__(self, map_name:str):
        self.map = []

        if not os.path.exists(map_name):
            logging.error("\nNo map file is found!")
            sys.exit()

        with open(map_name, "r") as file_content:
            lines = file_content.readlines()
            self.rows,self.cols=int(lines[1].split()[1]), int(lines[2].split()[1])
            for x, line in enumerate(lines[4:]):
                self.map.append([])
                for y, char in enumerate(line.strip()):
                    self.map[x].append(char)

    def get_loc_id(self, x,y):
        return x*self.cols+y
    
    def get_loc_xy(self, id):
        x = id//self.cols
        y = id % self.cols
        return x,y
    
    def getInnerNodes(self):
        self.innerNodes = []
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.check2neighbourS(x,y):
                    self.innerNodes.append(self.get_loc_id(x,y))
        self.nodes = self.innerNodes

    def check2neighbourS(self,x,y):
        if self.map[x][y] == ".":
            counterS = 0
            if x > 0 and self.map[x-1][y] == "S":
                counterS += 1
            if x < self.rows-1 and self.map[x+1][y] == "S":
                counterS += 1
            if y > 0 and self.map[x][y-1] == "S":
                counterS += 1
            if y < self.cols-1 and self.map[x][y+1] == "S":
                counterS += 1
            
            if counterS >= 2:
                return True
            else:
                return False
            
    def getOuterNodes(self, stationDistance=2):
        stationDistance += 1 #actual distance and not the fields in between like in fullfillment_config.yaml
        self.outerNodes = []
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y] == "E":
                    if x+stationDistance < self.rows and self.map[x+stationDistance][y] == "E":
                        self.outerNodes.append(self.get_loc_id(x+int(stationDistance/2),y))
                    elif y+stationDistance < self.cols and self.map[x][y+stationDistance] == "E":
                        self.outerNodes.append(self.get_loc_id(x,y+int(stationDistance/2)))
                    elif x-stationDistance >= 0 and self.map[x-stationDistance][y] == "E":
                        pass
                    elif y-stationDistance >= 0 and self.map[x][y-stationDistance] == "E":
                        pass
                    else:
                        self.outerNodes.append(self.get_loc_id(x,y))
        self.nodes = self.innerNodes + self.outerNodes
        

    
    def assignRegions(self):
        self.regions = []
        currentId = 0
        for x in range(len(self.map)):
            self.regions.append([])
            for y in range(len(self.map[x])):
                minIdx = -1
                minDist = 99999999
                for nodeIdx in range(len(self.nodes)):
                    if self.manhattan_dist(currentId, self.nodes[nodeIdx]) < minDist:
                        minIdx = nodeIdx
                        minDist = self.manhattan_dist(currentId, self.nodes[nodeIdx])
                self.regions[x].append(minIdx)
                currentId += 1

    def manhattan_dist(self,loc1,loc2):
        x1 = loc1 // self.cols 
        y1 = loc1 % self.cols 
        x2 = loc2 // self.cols 
        y2 = loc2 % self.cols  
        return abs(x1-x2)+abs(y1-y2)
    
    def createAdjacenyMatrix(self, includeOuterDistance, maxDistance=4, maxOuterDistance=10):
        self.AdjMatrix = []
        num_inner_nodes = len(self.innerNodes)
        if not includeOuterDistance:
            matrix_size = num_inner_nodes
        else:
            num_outer_nodes = len(self.outerNodes)
            matrix_size = num_inner_nodes + num_outer_nodes

        for i in range(matrix_size):
            self.AdjMatrix.append([0] * matrix_size)

        for i in range(num_inner_nodes):
            for j in range(num_inner_nodes):
                if self.manhattan_dist(self.innerNodes[i], self.innerNodes[j]) <= maxDistance:
                    self.AdjMatrix[i][j] = 1

        if includeOuterDistance:
            for i in range(num_outer_nodes):
                for j in range(num_outer_nodes):
                    if self.manhattan_dist(self.outerNodes[i], self.outerNodes[j]) <= maxOuterDistance:
                        self.AdjMatrix[num_inner_nodes + i][num_inner_nodes + j] = 1

            for n_out in range(num_outer_nodes):
                min_dist = 99999999
                for n_inn in range(num_inner_nodes):
                    dist = self.manhattan_dist(self.outerNodes[n_out], self.innerNodes[n_inn])
                    if dist < min_dist:
                        min_dist = dist
                for n_inn in range(num_inner_nodes):
                    if self.manhattan_dist(self.outerNodes[n_out], self.innerNodes[n_inn]) <= min_dist + 1:
                        self.AdjMatrix[num_inner_nodes + n_out][n_inn] = 1
                        self.AdjMatrix[n_inn][num_inner_nodes + n_out] = 1

    def overwriteNodeLocationsWithRegionCenter(self):
        for i in range(len(self.nodes)):
            x_list = []
            y_list = []
            for x in range(len(self.map)):
                for y in range(len(self.map[x])):
                    if self.regions[x][y] == i:
                        if self.map[x][y] == "S" or self.map[x][y] == "E":
                            x_list.append(x)
                            y_list.append(y)
            new_x = int(sum(x_list)/len(x_list))
            new_y = int(sum(y_list)/len(y_list))
            if new_x > 0 and new_x < len(self.map) and new_y > 0 and new_y < len(self.map[0]):
                if self.map[new_x][new_y] != "@" and self.map[new_x][new_y] != "T":
                    self.nodes[i] = self.get_loc_id(new_x,new_y)
                else:
                    print(f"New region center for node {i} is occupied by obstacle, new center not set")
            else:
                print(f"New region center for node {i} is out of map, new center not set")
    
    def printNodeCheckMap(self, file):
        checkMap = self.map.copy()
        for x in range(len(checkMap)):
            for y in range(len(checkMap[x])):
                loc_id = self.get_loc_id(x,y)
                if loc_id in self.nodes:
                    node = self.nodes.index(loc_id)
                    checkMap[x][y] = str(node%10)
        for x in range(len(checkMap)):
            file.write("".join(checkMap[x])+"\n")
        print("Node check map printed to file")



    def saveInFile(self, args):
        with open(args.outputFile,"w") as file:
            file.write("height "+str(self.rows)+"\n")
            file.write("width "+str(self.cols)+"\n")
            file.write("nNodes "+str(len(self.nodes))+"\n")
            file.write("nInnerNodes "+str(len(self.innerNodes))+"\n")
            file.write(",".join(str(node) for node in self.nodes) + "\n")
            for x in range(len(self.regions)):
                file.write(",".join(str(elem) for elem in self.regions[x]) + "\n")
            for i in range(len(self.AdjMatrix)):
                file.write(",".join(str(elem) for elem in self.AdjMatrix[i]) + "\n")
            if args.includeCheckMap:
                self.printNodeCheckMap(file)
            
    
        print("successfully saved as",args.outputFile)


    






def parse_arguments():
    parser = argparse.ArgumentParser(description='Script Parameters')
    parser.add_argument('--mapFile', help='Map file name', required=True)
    parser.add_argument('--outputFile', help='Output file name', default="nodes.nodes")
    parser.add_argument('--centerNodes', help='Adjusts the node locations to the center of their regions', action='store_true')
    parser.add_argument('--includeCheckMap', help='Add map at the end of the file that marks the locations of the nodes for visual check', action='store_true')
    parser.add_argument('--createOuterNodes', help='Also create nodes for the outer picking stations and not only for the storage grid. Not usefull. Dont center.', action='store_true')
    parser.add_argument('--stationDistance', help='Number of empty fields between the picking stations. For the current setup we almost always use 2. (See fullfillment_config.yaml)', default=2)
    parser.add_argument('--adjMatrixDistance', help='If the distance between two nodes is <= adjMatrixDistance, they are connected by an edge. For Obstacles with size 3x2 -> default value 4 makes sense.', default=4)
    parser.add_argument('--adjMatrixDistanceOuterCircle', help='Max distance for the nodes on the outer circle. 10 is good. Should not connect nonadjacent stations -> no circle anymore.', default=10)

    args = parser.parse_args()
    return args

# python3 script/createGraphNodes.py --mapFile "myWorld/warehouse_4x3.map" --outputFile "myWorld/warehouse_4x3_withOuter.nodes" --createOuterNodes --includeCheckMap
if __name__=="__main__":
    args=parse_arguments()
    GC = GraphCreator(args.mapFile)
    GC.getInnerNodes()
    if args.createOuterNodes:
        GC.getOuterNodes(args.stationDistance)
    GC.assignRegions()
    GC.createAdjacenyMatrix(args.createOuterNodes, args.adjMatrixDistance, args.adjMatrixDistanceOuterCircle)
    if args.centerNodes:
        GC.overwriteNodeLocationsWithRegionCenter()
    GC.saveInFile(args)