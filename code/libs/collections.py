
class Singleton(object):

    def __init__(self, cls):
        self.cls = cls
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = self.cls(*args, **kwargs)
        return self.instance

    def __repr__(self):
        return repr(self.cls)


class _Node(object):

    def __init__(self, obj, next_=None, prev=None):
        self.obj = obj
        self.next = next_
        self.prev = prev

    def __repr__(self):
        return '{}(obj={})'.format(type(self).__name__, repr(self.obj))


class DoubleLinkList(object):

    def __init__(self):
        self.__root = _Node(None)
        self.__root.next = self.__root
        self.__root.prev = self.__root

    def __iter__(self):
        curr = self.__root.next
        while curr != self.__root:
            yield curr
            curr = curr.next

    def __len__(self):
        result = 0
        for _ in self:
            result += 1
        return result

    def is_empty(self):
        return self.__root.next is None

    def add(self, obj):
        """Insert at head"""
        node = _Node(obj, next_=self.__root.next, prev=self.__root)
        self.__root.next.prev = node
        self.__root.next = node
        return node

    def append(self, obj):
        """Insert at tail"""
        node = _Node(obj, next_=self.__root, prev=self.__root.prev)
        self.__root.prev.next = node
        self.__root.prev = node
        return node

    def insert(self, obj1, obj2):
        """Insert at specified position (insert obj2 before obj1)

        :param obj1: Node data element
        :param obj2: Node data element
        :return: _Node containing obj2
        """
        pos = self.search(obj2)
        if pos is None:
            raise ValueError('{} not in list'.format(obj1))
        node = _Node(obj2, next_=pos, prev=pos.prev)
        pos.prev.next = node
        pos.prev = node
        return node

    def search(self, obj):
        """Find the node containing the specified data (obj type must implement __eq__)

        :param obj: Data element of the linked list node
        :return: _Node instance or None
        """
        for node in self:
            if node.obj == obj:
                return node

    def remove(self, obj):
        """Remove the node containing the specified object

        :param obj: Data element of the linked list node
        :return: None
        :raise: ValueError if element node does not exist
        """
        node = self.search(obj)
        if node is None:
            raise ValueError('{} not in link'.format(obj))
        node.prev.next = node.next
        node.next.prev = node.prev


class OrderedDict(object):

    def __init__(self, iterable=None):
        self.__keys_link = DoubleLinkList()
        self.__key_node_map = {}
        self.__storage = {}
        if isinstance(iterable, (tuple, list)):
            self.__load(iterable)

    def __load(self, sequence):
        for k, v in sequence:
            self[k] = v

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, [(k, v) for k, v in self.items()])

    def __iter__(self):
        return (node.obj for node in self.__keys_link)

    def __setitem__(self, key, value):
        if key not in self.__storage:
            self.__key_node_map[key] = self.__keys_link.append(key)
        self.__storage[key] = value

    def __getitem__(self, item):
        return self.__storage[item]

    def __delitem__(self, key):
        del self.__storage[key]
        node = self.__key_node_map.pop(key)
        node.prev.next = node.next
        node.next.prev = node.prev

    def keys(self):
        return iter(self)

    def values(self):
        return (self.__storage[key] for key in self)

    def items(self):
        return ((k, self.__storage[k]) for k in self)

    def get(self, key, default=None):
        if key not in self.__storage:
            return default
        return self.__storage[key]

    def pop(self, key, default=None):
        if key not in self.__storage:
            return default
        temp = self[key]
        del self[key]
        return temp

    def update(self, obj):
        for k, v in obj.items():
            self[k] = v

    def setdefault(self, key, value):
        if key in self.__storage:
            return self[key]
        else:
            self[key] = value
            return value


class Integer(object):
    """serialize signed/unsigned Integer to/from bytes"""

    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    def toBytes(self, length=1, byteorder='big', signed=False):
        if byteorder == 'little':
            order = range(length)
        elif byteorder == 'big':
            order = reversed(range(length))
        else:
            raise ValueError("byteorder must be either 'little' or 'big'")
        return bytes((self.value >> i * 8) & 0xff for i in order)

    @classmethod
    def fromBytes(cls, raw, byteorder='big', signed=False):
        if byteorder == 'little':
            little_ordered = list(raw)
        elif byteorder == 'big':
            little_ordered = list(reversed(raw))
        else:
            raise ValueError("byteorder must be either 'little' or 'big'")
        n = sum(b << i * 8 for i, b in enumerate(little_ordered))
        if signed and little_ordered and (little_ordered[-1] & 0x80):
            n -= 1 << 8 * len(little_ordered)
        return n
