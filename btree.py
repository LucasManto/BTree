ORDER = 6
NODE_SIZE = -1 + (14*ORDER)


class TreeNode():
    def __init__(self, string=''):
        if string == '':
            self.count = 0
            self.keys = [-1] * ORDER
            self.children = [-1] * ORDER
            self.data_rrn = [-1] * ORDER
        else:
            nodeStrings = string.split('|')
            self.count = int(nodeStrings[0])
            self.keys = [int(key) for key in nodeStrings[1].split(' ')]
            self.keys.insert(0, None)
            self.children = [int(child) for child in nodeStrings[2].split(' ')]
            self.data_rrn = [int(rrn) for rrn in nodeStrings[3].split(' ')]
            self.data_rrn.insert(0, None)

    def __str__(self):
        count_str = str(self.count).zfill(5)

        keys_str = ''
        for key in self.keys[1:-1]:
            keys_str = keys_str + str(key).zfill(3) + ' '
        keys_str = keys_str + str(self.keys[-1]).zfill(3)

        children_str = ''
        for child in self.children[0:-1]:
            children_str = children_str + str(child).zfill(5) + ' '
        children_str = children_str + str(self.children[-1]).zfill(5)

        data_rrn_str = ''
        for rrn in self.data_rrn[1:-1]:
            data_rrn_str = data_rrn_str + str(rrn).zfill(3) + ' '
        data_rrn_str = data_rrn_str + str(self.data_rrn[-1]).zfill(3)

        return '{}|{}|{}|{}\n'.format(count_str, keys_str, children_str, data_rrn_str)

    def searck_key(self, key):
        if key < self.keys[1]:
            return False, 0

        pos = self.count
        while pos > 1:
            if key >= self.keys[pos]:
                break
            pos -= 1
        
        return (self.keys[pos] == key), pos


def search_in_tree(key):
    with open('arvore.ndx', 'r') as index_file:
        root = root = int(index_file.readline())
        return search_in_tree_recursive(key, root, 0, index_file)


def search_in_tree_recursive(key, root, pos, index_file):
    if root == -1:
        return -1

    node = return_node(index_file, root)

    result, pos = node.searck_key(key)
    if result:
        return root

    return search_in_tree_recursive(key, node.children[pos], pos, index_file)


def return_node(index_file, root):
    index_file.seek(7 + NODE_SIZE*root)
    return TreeNode(index_file.readline())


if __name__ == '__main__':

    b = TreeNode()
    b.count = 2
    b.keys = [-1, 10, 20, -1, -1, -1]
    b.children = [1, 2, -1, -1, -1, -1]

    c = TreeNode()
    c.count = 1
    c.keys = [-1, 5, -1, -1, -1, -1]

    d = TreeNode()
    d.count = 1
    d.keys = [-1, 15, -1, -1, -1, -1]

    e = None

    with open('arvore.ndx', 'w') as index_file:
        index_file.write('{}\n'.format('0'.zfill(5)))
        index_file.write(str(b))
        index_file.write(str(c))
        index_file.write(str(d))

    with open('arvore.ndx', 'r') as index_file:
        root = search_in_tree(16)
        print(root)
