import pickle
import sys


NODE_SIZE = 83


class TreeNode():
    def __init__(self):
        self.count = 0
        self.keys = [-1, -1, -1, -1, -1, -1]
        self.children = [-1] * 6
        self.data_rrn = [-1] * 6


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

    with open('arvore.ndx', 'w') as index_file:
        index_file.write('{}\n'.format('2'.zfill(5)))
        index_file.write(str(b))
        index_file.write(str(c))
        index_file.write(str(d))

    with open('arvore.ndx', 'r') as index_file:
        root = int(index_file.readline())
        index_file.seek(7+(NODE_SIZE*root))
        node = index_file.readline()
        print(node)