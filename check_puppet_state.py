#!/usr/bin/env python

import yaml
import sys
import time
import datetime

if len(sys.argv) != 5:
    print "%s: [max_old_minutes_warn] [max_old_minutes_crit] [failed_warn] [failed_crit]" %(sys.argv[0])
    print
    print "- max_old_minutes_warn     : warning if puppet was last run max_old_minutes_warn ago"
    print "- max_old_minutes_crit     : critical if puppet was last run max_old_minutes_crit ago"
    print "- failed_warn              : warning if number of failed resources is higher than failed_warn"
    print "- failed_crit              : critical if number of failed resources is higher than failed_crit"
    print
    print "If you don't need criticals, put 0 instead of real value"

    sys.exit(3) 

max_old_warn = int(sys.argv[1])
max_old_crit = int(sys.argv[2])
max_failed_warn = int(sys.argv[3])
max_failed_crit = int(sys.argv[4])

def construct_ruby_object(loader, suffix, node):
    return loader.construct_yaml_map(node)

def construct_ruby_sym(loader, node):
    return loader.construct_yaml_str(node)

state = '/var/lib/puppet/state/last_run_summary.yaml'

# Necessary to parse puppet yaml output
yaml.add_multi_constructor(u"!ruby/object:", construct_ruby_object)
yaml.add_constructor(u"!ruby/sym", construct_ruby_sym)

try:
	yaml_state_stream = file(state, 'r')
except:
	print "UNKNOWN: can't open %s" %(state)
	sys.exit(3)

try:
	yaml_state = yaml.load(yaml_state_stream)
except:
	print "WARNING: can't parse YAML output"
	sys.exit(1)

# Read some important parameters from state file
try:
	state_version_config = yaml_state['version']['config']
	state_version_puppet = yaml_state['version']['puppet']
	state_time_last_run = yaml_state['time']['last_run']
	state_event_failed = yaml_state['events']['failure']
	state_event_total = yaml_state['events']['total']
	state_res_failed = yaml_state['resources']['failed']
	state_res_total = yaml_state['resources']['total']
except: 
	print "WARNING: can't load all YAML values from state file"
	sys.exit(1)

# Calculate seconds from last run
last_run = int(time.time()) - state_time_last_run
last_run_str = str(datetime.timedelta(seconds=last_run))

exit_val = 0
exit_msg = "Last run: %s, Puppet: %s, Catalog: %s, Event-Failures: %s/%s, Resource-Falures: %s/%s" % (
	last_run_str, state_version_puppet, state_version_config, state_event_failed, state_event_total, state_res_failed,
	state_res_total )

if max_old_crit != 0 and last_run >= max_old_crit*60:
	exit_msg = "CRITICAL: last_run older than %dm (%s)" % (max_old_crit, exit_msg)
	exit_val = 2
elif last_run >= max_old_warn*60:
	exit_msg = "WARNING: last_run older than %dm (%s)" % (max_old_warn, exit_msg)
	exit_val = 1
elif max_failed_crit != 0 and state_event_failed + state_res_failed >= max_failed_crit:
	exit_msg = "CRITICAL: more than %d failed (%s)" % (max_failed_crit, exit_msg)
	exit_val = 2
elif state_event_failed + state_res_failed >= max_failed_warn:
	exit_msg = "WARNING: more than %d failed (%s)" % (max_failed_warn, exit_msg)
	exit_val = 1
else:
	exit_msg = "OK: %s" % (exit_msg)
	exit_val = 0

print exit_msg
sys.exit(exit_val)
