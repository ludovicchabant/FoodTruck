import logging
import subprocess
from .base import SourceControl, RepoStatus


logger = logging.getLogger(__name__)


def _s(strs):
    """ Convert a byte array to string using UTF8 encoding. """
    if strs is None:
        return None
    assert isinstance(strs, bytes)
    return strs.decode('utf8')


class MercurialSourceControl(SourceControl):
    def __init__(self, root_dir):
        super(MercurialSourceControl, self).__init__(root_dir)
        self.hg = 'hg'

    def getStatus(self):
        res = RepoStatus()
        st_out = self._run('status')
        for line in st_out.split('\n'):
            if len(line) == 0:
                continue
            if line[0] == '?' or line[0] == 'A':
                res.new_files.append(line[2:])
            elif line[0] == 'M':
                res.edited_files.append(line[2:])
        return res

    def commit(self, rel_paths, message):
        raise NotImplementedError()

    def _run(self, cmd, *args, **kwargs):
        exe = [self.hg, '-R', self.root_dir]
        exe.append(cmd)
        exe += args
        logger.debug("Running Mercurial: " + str(exe))
        out = subprocess.check_output(exe)
        encoded_out = _s(out)
        return encoded_out

