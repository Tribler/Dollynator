from anytree import Node


def get_children(curr_state):
    return curr_state.children


def get_parent(curr_state):
    return curr_state.parent


def get_no_replications(curr_state):
    return curr_state.depth


def get_curr_state(tree, nick):
    for elem in tree:
        if elem.name == nick:
            return elem


def add_child(tree, child_name, parent=None):
    child = Node(child_name, parent=parent)
    tree.append(child)
    return tree


def create_child_name(provider, option, transaction_hash):
    return str(provider) + "|" + str(option) + "|" + str(transaction_hash)
