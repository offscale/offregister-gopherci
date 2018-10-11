import sys
from functools import partial
from os import path

from fabric.context_managers import cd
from fabric.operations import run
from offregister_fab_utils.apt import apt_depends
from offregister_fab_utils.fs import cmd_avail
from offregister_fab_utils.git import clone_or_update
from offregister_fab_utils.ubuntu.systemd import install_upgrade_service
from offregister_go import ubuntu as go
from pkg_resources import resource_filename

hook_dir = partial(path.join, path.dirname(resource_filename(sys.modules[__name__].__name__, '__init__.py')), '_conf')


def install0(*args, **kwargs):
    apt_depends('git')
    go.install0()
    if not cmd_avail('glide'):
        run('curl https://glide.sh/get | sh')

    gopath = run('echo "$GOPATH"', quiet=True)

    to_dir = '{gopath}/src/github.com/bradleyfalzon/gopherci'.format(gopath=gopath)
    clone_or_update('gopherci', team='SamuelMarks', branch='master', to_dir=to_dir, skip_clean=True, skip_reset=True)
    with cd(to_dir):
        run('glide i')
        run('go build && mv gopherci $GOPATH/bin')

    to_dir = '{gopath}/src/github.com/bradleyfalzon/gopherci-web'.format(gopath=gopath)
    clone_or_update('gopherci-web', team='SamuelMarks', branch='false-stripes', to_dir=to_dir,
                    skip_clean=True, skip_reset=True)
    with cd(to_dir):
        run('glide i')
        run('go build && mv gopherci-web {gopath}/bin'.format(gopath=gopath))

    return {'installed': ('gopherci', 'gopherci-web')}


def services1(*args, **kwargs):
    gopath = run('echo "$GOPATH"', quiet=True)
    group, user = run('''printf '%s:%s' "$USER" $(id -gn)''', shell_escape=False, quiet=True).split(':')
    return {service: install_upgrade_service(service,
                                             {'ExecStart': '{gopath}/bin/{service}'.format(gopath=gopath,
                                                                                           service=service),
                                              'WorkingDirectory': gopath,
                                              'User': user, 'Group': group or user,
                                              'Environments': 'Environment=GOPATH={gopath}'.format(gopath=gopath),
                                              'service_name': service}
                                             )
            for service in ('gopherci', 'gopherci-web')}
