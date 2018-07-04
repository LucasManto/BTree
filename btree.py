import sys
import os

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

    def insert(self, key, rrn, rightNode, pos):
        self.keys.insert(pos+1, key)
        self.data_rrn.insert(pos+1, rrn)
        self.children.insert(pos+1, rightNode)

        self.keys.pop(-1)
        self.data_rrn.pop(-1)
        self.children.pop(-1)

        self.count += 1

    def remove(self, pos):
        self.keys.pop(pos)
        self.data_rrn.pop(pos)
        self.children.pop(pos)

        self.keys.append(-1)
        self.data_rrn.append(-1)
        self.children.append(-1)

        self.count -= 1


class BTree():
    def __init__(self, file_name='arvore.ndx'):
        self.__file_name = file_name
        self.__node_count = 0
        
        try:
            with open(self.__file_name) as index_file:
                pass
        except Exception:
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

    def insert(self, key, rrn):
        root = self.__get_root()

        result, middleKey, rrn, rightNode = self.__overflow(key, rrn, root)
        if result:
            node = TreeNode()
            node.insert(key, rrn, -1, 0)
            node.keys[1] = middleKey
            node.data_rrn[1] = rrn
            node.children[0] = root
            node.children[1] = rightNode
            self.__write(node, True)

    def __overflow(self, key, rrn, root):
        if root == -1:
            middleKey = key
            rightNode = -1
            return True, middleKey, rrn, rightNode
        
        pos = -1
        root_node = self.return_node(root)
        result, pos = root_node.searck_key(key)

        result, middleKey, rrn, rightNode = self.__overflow(key, rrn, root_node.children[pos])
        if result:
            if root_node.count < MAX:
                root_node.insert(middleKey, rrn, rightNode, pos)
                self.__update(root, root_node)
                return False, middleKey, rrn, rightNode
            else:
                middleKey, newRrn, rightNode = self.__split(middleKey, rrn, rightNode, root, pos)
                return True, middleKey, newRrn, rightNode
        return False, -1, -1, -1

    def __split(self, middleKey, rrn, rightNode, root, pos):
        cut_spot = -1
        if pos < MIN:
            cut_spot = MIN
        else:
            cut_spot = MIN + 1

        root_node = self.return_node(root)

        newRightNode = TreeNode()
        for i in range(cut_spot + 1, root_node.count + 1):
            newRightNode.keys[i - cut_spot] = root_node.keys[i]
            newRightNode.data_rrn[i - cut_spot] = root_node.data_rrn[i]
            newRightNode.children[i - cut_spot] = root_node.children[i]
            
            root_node.keys[i] = -1
            root_node.data_rrn[i] = -1
            root_node.children[i] = -1

        newRightNode.count = root_node.count - cut_spot
        root_node.count = cut_spot

        if pos <= MIN:
            root_node.insert(middleKey, rrn, rightNode, pos)
        else:
            newRightNode.insert(middleKey, rrn, rightNode, pos - cut_spot)

        newMiddleKey = root_node.keys[root_node.count]
        newRrn = root_node.data_rrn[root_node.count]
        newRightNode.children[0] = root_node.children[root_node.count]

        root_node.keys[root_node.count] = -1
        root_node.data_rrn[root_node.count] = -1
        root_node.children[root_node.count] = -1
        root_node.count -= 1

        self.__update(root, root_node)
        self.__write(newRightNode)

        return newMiddleKey, newRrn, self.__node_count-1

    def remove(self, key):
        with open(self.__file_name, 'r+') as index_file:
            root = int(index_file.readline())
            self.__remove_recursive(key, root)

    def __remove_recursive(self, key, root):
        if root == -1:
            return

        root_node = self.return_node(root)
        result, pos = root_node.searck_key(key)
        if result:
            if root_node.children[pos] != -1:
                self.__promoteNextKey(root, pos)
                root_node = self.return_node(root)
                self.__remove_recursive(root_node.keys[pos], root_node.children[pos])
            else:
                root_node.remove(pos)
                self.__update(root, root_node)
        else:
            self.__remove_recursive(key, root_node.children[pos])

        if root_node.children[pos] != -1:
            child = root_node.children[pos]
            child_node = self.return_node(child)
            if child_node.count < MIN:
                self.__restore(root, pos)
                root_node = self.return_node(root)
                if root_node.count == 0:
                    self.__update(root, root_node, True)

    def __restore(self, root, pos):
        root_node = self.return_node(root)

        if pos == 0:
            sibling = root_node.children[1]
            sibling_node = self.return_node(sibling)
            if sibling_node.count > MIN:
                self.__move_to_left(root, 1)
            else:
                self.__combine_siblings(root, 1)
        else:
            if pos == root_node.count:
                sibling = root_node.children[pos - 1]
                sibling_node = self.return_node(sibling)

                if sibling_node.count > MIN:
                    self.__move_to_right(root, pos)
                else:
                    self.__combine_siblings(root, pos)
            else:
                sibling_left = root_node.children[pos - 1]
                sibling_left_node = self.return_node(sibling_left)
                sibling_right = root_node.children[pos + 1]
                sibling_right_node = self.return_node(sibling_right)

                if sibling_left_node.count > MIN:
                    self.__move_to_right(root, pos)
                elif sibling_right_node.count > MIN:
                    self.__move_to_left(root, pos + 1)
                else:
                    self.__combine_siblings(root, pos)

    def __combine_siblings(self, root, pos):
        root_node = self.return_node(root)
        left_child = root_node.children[pos - 1]
        left_child_node = self.return_node(left_child)
        right_child = root_node.children[pos]
        right_child_node = self.return_node(right_child)

        left_child_node.count += 1
        left_child_node.keys[left_child_node.count] = root_node.keys[pos]
        left_child_node.data_rrn[left_child_node.count] = root_node.data_rrn[pos]
        left_child_node.children[left_child_node.count] = right_child_node.children[0]

        for i in range(1, right_child_node.count + 1):
            left_child_node.count += 1
            left_child_node.keys[left_child_node.count] = right_child_node.keys[i]
            left_child_node.data_rrn[left_child_node.count] = right_child_node.data_rrn[i]
            left_child_node.children[left_child_node.count] = right_child_node.children[i]

        root_node.keys.pop(pos)
        root_node.data_rrn.pop(pos)
        root_node.children.pop(pos)

        root_node.keys.append(-1)
        root_node.data_rrn.append(-1)
        root_node.children.append(-1)

        root_node.count += 1

        right_child_node = TreeNode()

        self.__update(root, root_node)
        self.__update(left_child, left_child_node)
        self.__update(right_child, right_child_node)

    def __move_to_right(self, root, pos):
        root_node = self.return_node(root)
        right_child = root_node.children[pos]
        right_child_node = self.return_node(right_child)

        right_child_node.keys.insert(0, -1)
        right_child_node.data_rrn.insert(0, -1)
        right_child_node.children.insert(0, -1)

        right_child_node.keys.pop(-1)
        right_child_node.data_rrn.pop(-1)
        right_child_node.children.pop(-1)

        right_child_node.count += 1
        right_child_node.keys[1] = root_node.keys[pos]
        right_child_node.data_rrn[1] = root_node.data_rrn[pos]

        sibling = root_node.children[pos - 1]
        sibling_node = self.return_node(sibling)

        root_node.keys[pos] = sibling_node.keys[sibling_node.count]
        root_node.data_rrn[pos] = sibling_node.data_rrn[sibling_node.count]
        sibling_node.keys.remove(sibling_node.keys[sibling_node.count])
        sibling_node.data_rrn.remove(sibling_node.data_rrn[sibling_node.count])
        sibling_node.keys.append(-1)
        sibling_node.data_rrn.append(-1)
        sibling_node.count -= 1

        self.__update(root, root_node)
        self.__update(right_child, right_child_node)
        self.__update(sibling, sibling_node)

    def __move_to_left(self, root, pos):
        root_node = self.return_node(root)
        left_child = root_node.children[pos - 1]
        left_child_node = self.return_node(left_child)

        left_child_node.count += 1
        left_child_node.keys[left_child_node.count] = root_node.keys[pos]
        left_child_node.data_rrn[left_child_node.count] = root_node.data_rrn[pos]

        sibling = root_node.children[pos]
        sibling_node = self.return_node(sibling)
        left_child_node.children[left_child_node.count] = sibling_node.children[0]

        root_node.keys[pos] = sibling_node.keys[1]
        root_node.data_rrn[pos] = sibling_node.data_rrn[1]

        sibling_node.keys.remove(sibling_node.keys[1])
        sibling_node.data_rrn.remove(sibling_node.data_rrn[1])
        sibling_node.keys.append(-1)
        sibling_node.data_rrn.append(-1)
        sibling_node.count -= 1

        self.__update(root, root_node)
        self.__update(left_child, left_child_node)
        self.__update(sibling, sibling_node)

    def __promoteNextKey(self, root, pos):
        with open(self.__file_name, 'r+') as index_file:
            root_node = self.return_node(root, index_file)
            leaf = root_node.children[pos]
            leaf_node = self.return_node(leaf, index_file)
            while leaf_node.children[0] != -1:
                leaf = leaf_node.children[0]
                leaf_node = self.return_node(leaf, index_file)
            root_node.keys[pos] = leaf_node.keys[1]
            root_node.data_rrn[pos] = leaf_node.data_rrn[1]
            self.__update(root, root_node)

    def __write(self, node, is_root=False):
        with open(self.__file_name, 'a') as index_file:
            index_file.write(str(node))
            self.__node_count += 1

        if is_root:
            with open(self.__file_name, 'r+') as index_file:
                node_id = self.__node_count - 1
                index_file.seek(0)
                index_file.write('{}\n'.format(str(node_id).zfill(5)))

    def __update(self, node_id, node, isRoot=False):
        with open(self.__file_name, 'r+') as index_file:
            index_file.seek(7+NODE_SIZE*node_id)
            index_file.write(str(node))
        
        if isRoot:
            with open(self.__file_name, 'r+') as index_file:
                index_file.write('{}\n'.format(str(node_id).zfill(5)))

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


def get_formatted_db_file():
    formatted_lines = []
    with open('./TabelaInicial.txt') as data_file:
        lines = data_file.readlines()
        for line in lines:
            line = line.split('|')
            line = [word.strip() for word in line]
            formatted_lines.append(line)
    return formatted_lines


def generate_db_file():
    formatted_lines = get_formatted_db_file()
    with open('./dados.txt', 'w') as data_file:
        for line in formatted_lines[3:-1]:
            write_line = '{}|{}|{}|#\n'.format(line[1], line[2], line[3])
            data_file.write(write_line)


def generate_index_file():
    try:
        os.remove('./primario.ndx')
    except Exception:
        pass
    tree = BTree('primario.ndx')
    with open('./dados.txt') as data_file:
        lines = data_file.readlines()
        rrn = 0
        for data in lines:
            prim_key = data.split('|')[0]
            if '$' in prim_key:
                rrn += len(data) + 1
                continue
            tree.insert(int(prim_key), rrn)
            rrn += len(data) + 1
    return tree


def insert(code, name, vehicle, tree):
    code = int(code)
    rrn = tree.search(code)
    if rrn is -1:
        data = '{}|{}|{}|#\n'.format(str(code).zfill(3), name, vehicle)
        with open('./dados.txt', 'a') as data_file:
            rrn = data_file.tell()
            data_file.write(data)
        tree.insert(code, rrn)
        print('\nDados registrados!\n')
    else:
        print('\nO codigo ja existe, escolha outro. Retornando para o menu...\n')


def search_data(code, tree):
    code = int(code)
    rrn = tree.search(code)
    
    if rrn is not -1:
        node = tree.return_node(rrn)
        index = node.keys.index(code)
        data_rrn = node.data_rrn[index]

        with open("./dados.txt", "r") as data_file:
            data_file.seek(data_rrn)
            data = data_file.readline()
            data = data.split('|')
            return data[:-1]
    else:
        return False


def remove_data(code, tree):
    code = int(code)
    rrn = tree.search(code)

    if rrn is -1:
        print('\nDados nao encotrados. Retornando ao menu...\n')
    else:
        node = tree.return_node(rrn)
        index = node.keys.index(code)
        data_rrn = node.data_rrn[index]

        with open('./dados.txt', 'r+') as data_file:
            data_file.seek(data_rrn)
            data_file.write('$')
        tree.remove(code)

def alter_data(code, tree):
    code = int(code)
    rrn = tree.search(code)

    if rrn is -1:
        print('\nDados nao encotrados. Retornando ao menu...\n')
    else:
        data = search_data(code, tree)

        code = data[0]
        name = data[1]
        vehicle = data[2]
        codigo = code

        print('Alterar: Codigo (1), Nome (2), Veiculo (3)')
        sys.stdout.write("Opcao: ")
        option = input()

        if option == '1':
            sys.stdout.write("  Novo Codigo: ")
            codigo = input()
            rrn = search_data(codigo, tree)
            if rrn:
                print('\nO codigo ja existe, escolha outro. Retornando para o menu...\n')
                return
        elif option == '2':
            sys.stdout.write("  Novo Nome: ")
            name = input()
        elif option == '3':
            sys.stdout.write("  Novo Veiculo: ")
            vehicle = input()
        remove_data(code, tree)
        insert(codigo, name, vehicle, tree)


def compress(tree):
    with open('./compress.bkp', 'w') as compressed_file:
        with open('./primario.ndx') as index_file:
            index_file.readline()
            data = index_file.readlines()
            for d in data:
                node = TreeNode(d)
                for key in node.keys[1:]:
                    data = search_data(key, tree)
                    if data:
                        compressed_file.write('{}|{}|{}|#\n'.format(str(data[0]).zfill(3), data[1], data[2]))
    os.remove('./dados.txt')
    os.rename('compress.bkp', 'dados.txt')
    generate_index_file()


def menu(tree):
    option = -2
    while(option != 6):
        print("Menu:")
        print(" 1. Inserir")
        print(" 2. Remover")
        print(" 3. Alterar")
        print(" 4. Procurar")
        print(" 5. Compactar")
        print(" 6. Sair")
        sys.stdout.write("  Opcao: ")
        option = input()
        if option == "1":
            sys.stdout.write("  Codigo: ")
            codigo = input()
            sys.stdout.write("  Nome: ")
            nome = input()
            sys.stdout.write("  Veiculo: ")
            veiculo = input()
            insert(codigo, nome, veiculo, tree)
        if option == '2':
            sys.stdout.write("  Codigo: ")
            codigo = input()
            remove_data(codigo, tree)
        if option == '3':
            sys.stdout.write("  Codigo: ")
            codigo = input()
            alter_data(codigo, tree)
        if option == '4':
            sys.stdout.write("  Codigo: ")
            codigo = input()
            data = search_data(codigo, tree)
            if data:
                print('\nDados encontrados:')
                print(' Codigo: {}'.format(data[0]))
                print(' Nome: {}'.format(data[1]))
                print(' Veiculo: {}\n'.format(data[2]))
            else:
                print('\nDados nao encontrados\n\n')
        if option == '5':
            print('\nComprimindo arquivo de dados...\n\n')
            compress(tree)
            print('\nCompressao completa\n\n')
        if option == '6':
            os.remove('./primario.lock')
            exit()


if __name__ == '__main__':
    tree = None
    try:
        with open('./primario.lock') as lock:
            print("\nArquivo de indices corrompido, estamos restaurando-o.\n")
            tree = generate_index_file()
    except Exception:
        try:
            with open('./primario.ndx') as index_file:
                pass
        except Exception:
            generate_db_file()
            tree = generate_index_file()
    with open('./primario.lock', 'w') as lock:
        pass
    tree = BTree('primario.ndx')
    menu(tree)