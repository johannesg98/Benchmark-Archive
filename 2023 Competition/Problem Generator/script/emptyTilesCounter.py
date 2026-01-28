import argparse
import os
import logging
import sys

#self.get_loc_id(x,y,rows,cols)

class EmptyTileCounter:
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

    def count(self):
        empty_tiles = 0
        for x in range(self.rows):
            for y in range(self.cols):
                if self.map[x][y] != '@' and self.map[x][y] != 'T':
                    empty_tiles += 1
        return empty_tiles




def parse_arguments():
    parser = argparse.ArgumentParser(description='Script Parameters')
    parser.add_argument('--mapFile', help='Map file name', required=True)
    
    args = parser.parse_args()
    return args

# python3 script/emptyTilesCounter.py --mapFile "myWorld/warehouse_4x3.map"
if __name__=="__main__":
    args=parse_arguments()

    ETC = EmptyTileCounter(args.mapFile)
    num_empty_tiles = ETC.count()

    print(f"Number of empty tiles in map {args.mapFile}: {num_empty_tiles}")


    