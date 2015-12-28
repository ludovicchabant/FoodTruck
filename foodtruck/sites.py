import os
import os.path
import subprocess
from piecrust.app import PieCrust


class UnauthorizedSiteAccessError(Exception):
    pass


class Site(object):
    _bake_pid_filename = 'foodtruck_bake.pid'
    _bake_log_filename = 'foodtruck_bake.log'

    def __init__(self, name, root_dir, cfg):
        self.name = name
        self.root_dir = root_dir
        self.cfg = cfg
        self._piecrust_app = None
        self._scm = None
        self._bake_pid_path = os.path.join(root_dir, self._bake_pid_filename)
        self._bake_log_path = os.path.join(root_dir, self._bake_log_filename)

    @property
    def piecrust_app(self):
        if self._piecrust_app is None:
            s = PieCrust(self.root_dir)
            s.config.set('site/root', '/site/%s/' % self.name)
            self._piecrust_app = s
        return self._piecrust_app

    @property
    def scm(self):
        if self._scm is None:
            scm_type = self.cfg.get('scm', 'type')
            if scm_type == 'hg':
                from .scm.mercurial import MercurialSourceControl
                self._scm = MercurialSourceControl(self.root_dir)
            else:
                raise NotImplementedError()
        return self._scm

    @property
    def is_bake_running(self):
        return os.path.isfile(self._bake_pid_path)

    def addFile(self, rel_path, bin_data):
        path = os.path.join(self.root_dir, rel_path)
        if not path.startswith(self.root_dir):
            raise UnauthorizedSiteAccessError(path)

        if not isinstance(bin_data, bytes):
            raise Exception()

        with open(path, 'wb') as f:
            f.write(bin_data)

    def bake(self):
        bake_cmd = self.cfg.get('triggers', 'bake')
        bake_cmd += ' > ' + self._bake_log_path
        is_shell = self.cfg.getboolean('triggers', 'bake.is_shell',
                                       fallback='false')
        proc = subprocess.Popen(
                bake_cmd, cwd=self.root_dir, shell=is_shell)
        with open(self._bake_pid_path, 'w') as fp:
            fp.write(str(proc.pid))


class FoodTruckSites():
    def __init__(self, cfg):
        self._sites = {}
        self._site_dirs = {}
        self._cfg = cfg

    @property
    def default_site_name(self):
        return self._cfg.get('foodtruck', 'default_site')

    def get_root_dir(self, name=None):
        name = name or self._cfg.get('foodtruck', 'default_site')
        s = self._site_dirs.get(name)
        if s:
            return s

        scfg = self._cfg.getcomplex('sites', name)
        root_dir = scfg['path']
        if not os.path.isdir(root_dir):
            raise Exception("Site '%s' has an invalid path." % name)
        self._site_dirs[name] = root_dir
        return root_dir

    def get(self, name=None):
        name = name or self.default_site_name
        s = self._sites.get(name)
        if s:
            return s

        root_dir = self.get_root_dir(name)
        s = Site(name, root_dir, self._cfg)
        self._sites[name] = s
        return s

