import inspect


def is_relevant(obj):
    """Filter for the inspector to filter out non user defined functions/classes"""
    if hasattr(obj, '__name__') and obj.__name__ == 'type':
        return False
    if inspect.isfunction(obj) or inspect.isclass(obj) or inspect.ismethod(obj):
        return True


def print_docs(module):
    default = 'No doc string provided' # Default if there is no docstring, can be removed if you want
    flag = True

    for child in inspect.getmembers(module, is_relevant):
        if not flag: print('\n\n\n')
        flag = False # To avoid the newlines at top of output
        doc = inspect.getdoc(child[1])
        if not doc:
            doc = default
        print(child[0], doc, sep = '\n')

        if inspect.isclass(child[1]):
            for grandchild in inspect.getmembers(child[1], is_relevant):
                doc = inspect.getdoc(grandchild[1])
                if doc:
                    doc = doc.replace('\n', '\n    ')
                else:
                    doc = default 
                print('\n    ' + grandchild[0], doc, sep = '\n    ')


import your_module
print_docs(your_module)
