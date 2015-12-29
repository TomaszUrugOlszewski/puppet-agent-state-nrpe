Monitor Puppet Agent
====================

This is very minimal NRPE plugin to monitor puppet agent status basing on content
of /var/lib/puppet/state/last\_run\_summary.yaml


Example usage
-------------

Check if puppet was run in last 5 minutes (warn) or 10 minutes (crit)

    ./check_puppet_state.py 5 10 1 1

