ORDER = 6
NODE_SIZE = -1 + (14*ORDER)
MAX = ORDER - 1
MIN = int((ORDER / 2) - 1)


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

    def insert(self, key, rightNode, pos):
        self.keys.insert(pos+1, key)
        self.children.insert(pos+1, rightNode)

        self.keys.pop(-1)
        self.children.pop(-1)

        self.count += 1


class BTree():
    def __init__(self, file_name='arvore.ndx'):
        self.__file_name = file_name
        self.__node_count = 0
        with open(self.__file_name, 'w') as index_file:
            index_file.write('-1\n'.zfill(6))

    def search(self, key):
        with open(self.__file_name, 'r') as index_file:
            root = int(index_file.readline())
            return self.__search_recursive(key, root, index_file)

    def __search_recursive(self, key, root, index_file):
        if root == -1:
            return -1

        node = self.return_node(root, index_file)
        result, pos = node.searck_key(key)
        if result:
            return root

        return self.__search_recursive(key, node.children[pos], index_file)

    def insert(self, key):
        root = self.__get_root()

        result, middleKey, rightNode = self.__overflow(key, root)
        if result:
            node = TreeNode()
            node.insert(key, -1, 0)
            node.keys[1] = middleKey
            node.children[0] = root
            node.children[1] = rightNode
            self.__write(node, True)

    def __overflow(self, key, root):
        if root == -1:
            middleKey = key
            rightNode = -1
            return True, middleKey, rightNode
        
        pos = -1
        root_node = self.return_node(root)
        result, pos = root_node.searck_key(key)

        result, middleKey, rightNode = self.__overflow(key, root_node.children[pos])
        if result:
            if root_node.count < MAX:
                root_node.insert(middleKey, rightNode, pos)
                self.__update(root, root_node)
                return False, middleKey, rightNode
            else:
                middleKey, rightNode = self.__split(middleKey, rightNode, root, pos)
                return True, middleKey, rightNode
        return False, -1, -1

    def __split(self, middleKey, rightNode, root, pos):
        cut_spot = -1
        if pos < MIN:
            cut_spot = MIN
        else:
            cut_spot = MIN + 1

        root_node = self.return_node(root)

        newRightNode = TreeNode()
        for i in range(cut_spot + 1, root_node.count + 1):
            newRightNode.keys[i - cut_spot] = root_node.keys[i]
            newRightNode.children[i - cut_spot] = root_node.children[i]
            
            root_node.keys[i] = -1
            root_node.children[i] = -1

        newRightNode.count = root_node.count - cut_spot
        root_node.count = cut_spot

        if pos <= MIN:
            root_node.insert(middleKey, rightNode, pos)
        else:
            newRightNode.insert(middleKey, rightNode, pos - cut_spot)

        newMiddleKey = root_node.keys[root_node.count]
        newRightNode.children[0] = root_node.children[root_node.count]

        root_node.keys[root_node.count] = -1
        root_node.children[root_node.count] = -1
        root_node.count -= 1

        self.__update(root, root_node)
        self.__write(newRightNode)

        return newMiddleKey, self.__node_count-1


    def __write(self, node, is_root=False):
        with open(self.__file_name, 'a') as index_file:
            index_file.write(str(node))
            self.__node_count += 1

        if is_root:
            with open(self.__file_name, 'r+') as index_file:
                node_id = self.__node_count - 1
                index_file.seek(0)
                index_file.write('{}\n'.format(str(node_id).zfill(5)))

    def __update(self, node_id, node):
        with open(self.__file_name, 'r+') as index_file:
            index_file.seek(7+NODE_SIZE*node_id)
            index_file.write(str(node))

    def __get_root(self):
        root = ''
        with open(self.__file_name, 'r') as index_file:
            root = index_file.readline()
        return int(root)

    def return_node(self, node, index_file=None):
        if node < 0:
            return None

        if index_file is None:
            with open(self.__file_name, 'r') as index_file:
                index_file.seek(7+NODE_SIZE*node)
                return TreeNode(index_file.readline())
        else:
            index_file.seek(7+NODE_SIZE*node)
            return TreeNode(index_file.readline())


if __name__ == '__main__':
    tree = BTree()
    tree.insert(10)
    tree.insert(11)
    tree.insert(12)
    tree.insert(13)
    tree.insert(14)
    tree.insert(15)
    tree.insert(9)
    tree.insert(8)
    tree.insert(16)
    tree.insert(17)
    tree.insert(18)
