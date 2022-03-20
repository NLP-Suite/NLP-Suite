# written by Mino Cha March 2022
# class for Tree nodes
class Node:
    def __init__(self,start):
        self.start = start
        self.children = []
        self.text = ''

# make a tree        
def make_tree(s):
    stack = []
    nodes = []
    cur = None
    root = None    

    for i, c in enumerate(s):
        if c == '(':
            cur = Node(i)
            if stack:
                stack[-1].children.append(cur)
            stack.append(cur)

            if root is None:
                root = cur

        elif c == ')' and stack:
            topnode = stack.pop()

            text = s[topnode.start + 1: i]
            topnode.text = text

    return root

# list of leaves
def getLeavesAsList(node):
    result = []
    for child in node.children:
        result.extend(getLeavesAsList(child))
    if not result:
        return [node]

    return result

# list of children
def getChildrenAsList(node):
    result = []
    for child in node.children:
        result.append(child)
    if not result:
        return [node]

    return result

