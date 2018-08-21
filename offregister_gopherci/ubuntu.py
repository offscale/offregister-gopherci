import sys
from functools import partial
from os import path

from fabric.context_managers import cd
from fabric.operations import run
from offregister_fab_utils.fs import cmd_avail
from offregister_go import ubuntu as go
from pkg_resources import resource_filename

hook_dir = partial(path.join, path.dirname(resource_filename(sys.modules[__name__].__name__, '__init__.py')), '_conf')


def install_configure0(*args, **kwargs):
    go.install0()
    src = 'github.com/SamuelMarks/gopherci'
    if not cmd_avail('dep'):
        run('go get -u github.com/golang/dep/cmd/dep')
    if not cmd_avail('glide'):
        run('curl https://glide.sh/get | sh')
    run('go get {src}'.format(src=src), warn_only=True)

    '''
    with cd('$GOPATH/src/{src}'.format(src=src)):
        run('make')
    '''

    # return restart_systemd('webhook')
