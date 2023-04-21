def singleton(cls):
    instances = {}
    def getInstance(*args, **kvargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kvargs)
        return instances[cls]
    return getInstance
        