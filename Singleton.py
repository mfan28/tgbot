def singleton(cls):
    instances = {}
    def getInstance(*args):
        if cls not in instances:
            instances[cls] = cls(*args)
        return instances[cls]
    return getInstance
        