#!/usr/bin/env python3

import os
from subprocess import check_call
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__))+'/../lib')

from ops.charm import CharmBase
from ops.main import main
from ops.framework import StoredState
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus


class TimescaleDB(CharmBase):

    state = StoredState

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self)
        self.framework.observe(self.on.upgrade_charm, self)

    def on_install(self, event):
        if not hasattr(self.state, 'installed'):
            self.state.installed = False
        elif self.state.installed:
            return
        try:
            # test if postgresql installed yet
            if not os.path.exists('/var/lib/postgresql'):
                event.framework.model.unit.status = WaitingStatus('waiting for postgresql to be installed')
                event.defer()
                return
            check_call(['add-apt-repository', '-y', 'ppa:timescale/timescaledb-ppa'])
            check_call(['apt-get', 'update', '-qq'])
            if os.path.exists('/var/lib/postgresql/10'):
                check_call(['apt-get', 'install', '-y', 'timescaledb-postgresql-10', 'postgresql-server-dev-10'])
            elif os.path.exists('/var/lib/postgresql/11'):
                check_call(['apt-get', 'install', '-y', 'timescaledb-postgresql-11', 'postgresql-server-dev-11'])
            else:
                event.framework.model.unit.status = BlockedStatus('failed to find a compatible version of postgresql (10, 11)')
                event.defer()
                return
            check_call(['timescaledb-tune', '-yes'])
            check_call(['systemctl', 'restart', 'postgresql'])
            event.framework.model.unit.status = ActiveStatus()
            self.state.installed = True
        except Exception as e:
            event.framework.model.unit.status = BlockedStatus('{}: {}'.format("install failed", e))
            event.defer()

    def on_upgrade_charm(self, event):
        if not hasattr(self.state, 'installed'):
            self.on_install(event)
            return
        try:
            check_call(['apt-get', 'update', '-qq'])
            check_call(['apt-get', 'dist-upgrade', '-y'])
            event.framework.model.unit.status = ActiveStatus()
        except Exception as e:
            event.framework.model.unit.status = BlockedStatus('{}: {}'.format("upgrade failed", e))
            event.defer()


if __name__ == "__main__":
    main(TimescaleDB)
