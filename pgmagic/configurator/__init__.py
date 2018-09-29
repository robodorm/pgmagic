class Config(type):
    _instances = {}

    def __call__(cls, *a, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(Config, cls).__call__(*a, **kw)
        return cls._instances[cls]


def provide_config(config):
    def w(fn):
        def r(*a, **kw):
            c = config()
            return fn(*a, **kw, cfg=c)
        return r
    return w
