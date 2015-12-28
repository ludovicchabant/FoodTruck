import configparser


class FoodTruckConfigNotFoundError(Exception):
    pass


class FoodTruckConfig(object):
    def __init__(self, cfg_path, defaults_path):
        self.cfg_path = cfg_path
        self.cfg = configparser.ConfigParser()
        try:
            if defaults_path:
                with open(defaults_path, 'r', encoding='utf8') as fp:
                    self.cfg.read_file(fp)
            if cfg_path:
                with open(cfg_path, 'r', encoding='utf8') as fp:
                    self.cfg.read_file(fp)
        except OSError:
            raise FoodTruckConfigNotFoundError()

    def load_from_string(self, s, source='<string>'):
        self.cfg.read_string(s, source)

    def items(self, section=None):
        if section is None:
            return self.cfg.items()
        return self.cfg.items(section)

    def sections(self):
        return self.cfg.sections()

    def has_section(self, section):
        return self.cfg.has_section(section)

    def has_option(self, section, name):
        return self.cfg.has_option(section, name)

    def options(self, section):
        return self.cfg.options(section)

    def get(self, section, option, **kwargs):
        return self.cfg.get(section, option, **kwargs)

    def getboolean(self, section, option, **kwargs):
        return self.cfg.getboolean(section, option, **kwargs)

    def getcomplex(self, section, name):
        f = name + '.'
        items = self.cfg.items(section)
        res = {}
        for k, v in items:
            if k.startswith(f):
                res[k[len(f):]] = v
        return res

    def set(self, section, name, value):
        if not self.cfg.has_section(section):
            self.cfg.add_section(section)
        self.cfg.set(section, name, value)

    def save(self):
        with open(self.cfg_path, 'w', encoding='utf8') as fp:
            self.cfg.write(fp)

