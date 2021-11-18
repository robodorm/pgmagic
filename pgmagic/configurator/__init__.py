class Config(type):
    _instances = {}

    def __call__(cls, *a, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(Config, cls).__call__(*a, **kw)
        return cls._instances[cls]
