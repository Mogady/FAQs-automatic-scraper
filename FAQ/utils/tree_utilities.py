from collections import deque


def preorderTraversal(root):
    """
    function used to traverse non binary tree as preorder
    # https://www.geeksforgeeks.org/iterative-preorder-traversal-of-a-n-ary-tree/
    :param root: tree root element
    :return: list of nodes sorted by preorder
    """
    Stack = deque([])
    # 'Preorder'-> contains all the
    # visited nodes.
    Preorder = []
    Par = []
    Preorder.append(root)
    Stack.append(root)
    # if tree only one element
    if len(Stack[0]) == 0:
        return Preorder

    while len(Stack) > 0:
        # 'Flag' checks whether all the child
        # nodes have been visited.
        flag = 0
        # CASE 1- If Top of the stack is a leaf
        # node then remove it from the stack:
        if len((Stack[len(Stack) - 1])) == 0:
            X = Stack.pop()
            # CASE 2- If Top of the stack is
            # Parent with children:
        else:
            Par = Stack[len(Stack) - 1]
            # a)As soon as an unvisited child is
        # found(left to right sequence),
        # Push it to Stack and Store it in
        # Auxillary List(Marked Visited)
        # Start Again from Case-1, to explore
        # this newly visited child
        for i in range(0, len(Par)):
            if Par[i] not in Preorder:
                flag = 1
                Stack.append(Par[i])
                Preorder.append(Par[i])
                break
                # b)If all Child nodes from left to right
                # of a Parent have been visited
                # then remove the parent from the stack.
        if flag == 0:
            Stack.pop()
    return Preorder


def printPathsUtil(preorder, sum,
                   text_so_far, path, attr):
    """
    traverse a HTML tree in a preorder fashion and calculate the length of the text for a path until reaching a limit
    :param preorder: list of nodes sorted by preorder to loop on
    :param sum: the text length limit
    :param text_so_far: string hold all the text so far
    :param path: list with the current visited nodes
    :param attr: determine which text element to calculate on {text,tail}
    :return: list[nodes], string
    """
    # empty node
    if len(preorder) == 0:
        return path, text_so_far

    curr_node = preorder.pop(0)
    if attr == 'text':
        text_so_far += (curr_node.text or '')
    else:
        text_so_far += (curr_node.tail or '')

    new_lines_count = text_so_far.count('\n') * 10
    sum_so_far = len(text_so_far.split()) + new_lines_count

    # add current node to the path
    path.append(curr_node)
    if sum_so_far >= sum:
        return path, text_so_far

    path, text_so_far = printPathsUtil(preorder, sum,
                                       text_so_far, path, attr)

    return path, text_so_far
