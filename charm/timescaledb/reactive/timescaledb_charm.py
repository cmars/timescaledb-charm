import os
from subprocess import check_call

from charms.reactive import when_not, set_flag, hook

from charmhelpers.core import hookenv


@when_not('timescaledb-charm.installed')
def install_timescaledb_charm():
    # test if postgresql installed yet
    if not os.path.exists('/var/lib/postgresql'):
        hookenv.status_set('blocked',
            'waiting for postgresql to be installed')
        return
    check_call(['add-apt-repository', '-y', 'ppa:timescale/timescaledb-ppa'])
    check_call(['apt-get', 'update', '-qq'])
    if os.path.exists('/var/lib/postgresql/10'):
        check_call(['apt-get', 'install', '-y', 'timescaledb-postgresql-10'])
    elif os.path.exists('/var/lib/postgresql/11'):
        check_call(['apt-get', 'install', '-y', 'timescaledb-postgresql-11'])
    else:
        hookenv.status_set('blocked',
            'failed to find a compatible version of postgresql')
        return
    check_call(['timescaledb-tune', '-yes'])
    check_call(['systemctl', 'restart', 'postgresql'])
    hookenv.status_set('active', 'ready')
    set_flag('timescaledb-charm.installed')


@hook('upgrade-charm')
def upgrade():
    check_call(['apt-get', 'update', 'qq'])
    check_call(['apt-get', 'dist-upgrade', '-y'])
