class DictObject(object):
    '''
    Simple conversion to a Class.
    '''
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [DictObject(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, DictObject(b) if isinstance(b, dict) else b)

class DictToObject(object):
    def __init__(self, inputStructure:list):
        self.outputStructure = self.create(inputStructure)

    def create(self, inputList:list)-> list:
        outputStructure = []
        for entry in inputList:
            outputStructure.append(DictObject(entry))
        return outputStructure

    def __repr__(self):
        return '<{0}.incidents={1}  object at {2}>'.format(
            self.__class__.__name__, self.outputStructure, hex(id(self)))
