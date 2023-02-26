import inspect


# from https://stackoverflow.com/questions/11461356/issubclass-returns-false-on-the-same-class-imported-from-different-paths
def inherits_from(child, parent_name):
    if inspect.isclass(child):
        return parent_name in [c.__name__ for c in inspect.getmro(child)[1:]]
    return False
