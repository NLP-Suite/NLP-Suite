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

# number of leaves (a flat count)
#   len(getLeavesAsList(root)) is NOT this: that list is nested like the tree, so under a single ROOT it has 1 item
def countLeaves(node):
    if not node.children:
        return 1
    return sum(countLeaves(child) for child in node.children)

# list of leaves (nested like the tree)
def getLeavesAsList(node):
    result = []
    for child in node.children:
        result.append(getLeavesAsList(child))
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

