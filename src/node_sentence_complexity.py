# written by Mino Cha, March 2022

import tree as tr

class Node:
    def __init__(self, tree, isLeaf=False):
        self.Ysc = 0
        self.Fsc = 0
        self.parent = None
        self.leaf = False
        self.root = True

        self.kids = tr.getChildrenAsList(tree)
        # self.leaves = tr.getLeavesAsList(tr.make_tree(tree))
        self.children = []

        if isLeaf==False:
            for i,kid in enumerate(self.kids):
                # print(kid.children)
                if len(kid.children)==0:
                    self.children.append(Node(kid, True))
                else:
                    self.children.append(Node(kid))
                self.children[i].setParent(self)
                self.children[i].root = False

            if len(self.children)==0:
                self.leaf = True
        else:
            self.parent = None
            self.leaf = True
            # self.root = False
            self.kids = []
            self.children = []

    
    # ********* Yngve *********
    def calY(self):
        for i in range(0,len(self.children)):
            child = self.children[i]
            # print(len(self.children))
            x = self.getY() + len(self.children) - 1.0 - i
            # print(x)
            child.setY(x)
            if (self.children[i].isLeaf()): continue
            child.calY()

    def setY(self, yngve):
        self.Ysc = yngve
    
    def getY(self):
        return self.Ysc

    def sumY(self):
        if (self.isLeaf()):
            return self.Ysc
        add = 0
        for i in range(0, len(self.children)):
            add = add + self.children[i].sumY()
        return add

    # ********* Frazier *********
    def calF(self):
        x = self.getF() + 1.0 if self.isRoot()!=True else self.getF() + 1.5
        self.children[0].setF(x)

        for i in range(0,len(self.children)):
            child = self.children[i]
            if (i != 0):
                child.setF(0.0)
            if (child.isLeaf()!=True):
                child.calF()
                continue
            # withleaf = child.getF() - 1.0
            # child.setF(withleaf)

    def setF(self, frazier):
        self.Fsc = frazier
    
    def getF(self):
        return self.Fsc

    def sumF(self):
        if (self.isLeaf()):
            return self.Fsc
        add = 0
        for i in range(0, len(self.children)):
            add = add + self.children[i].sumF()
        return add


    # general functions
    def isLeaf(self):
        return self.leaf

    def isRoot(self):
        return self.root
    
    def setParent(self, p):
        self.parent = p

