#!/bin/env python
# -*- coding: utf-8 -*-
#
# Inspired (in its structure) by lots of weechat plugins.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Autosort automatically keeps your buffers sorted and grouped by server.
# You can define your own sorting rules. See /help autosort for more
# details.
#
# https://github.com/fmount/autoreply
#
#
# Changelog:
# 0.1:
#  - DEBUG mode is not a config parameter anymore
#  - cmd is now built before setting running w.command
#  - The server filter is ready

import time

IMPORT_OK = True
DEBUG = True

try:
    import weechat as w
except ImportError:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: http://www.weechat.org/")
    IMPORT_OK = False

"""
The autoreply plugin is built to make your life easier when
weechat is still in foreground but /away is set.
It makes sense to build an automated reply (with a custom
message) that works and is sent when the autoreply plugin
is activated.
This is inspired to a similar irssi plugin.
"""

SCRIPT_NAME = "autoreply"
SCRIPT_AUTHOR = "Francesco Pantano <fmount@inventati.org>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "BSD"
SCRIPT_DESC = "Simple autoreply on private channels when away"
SCRIPT_REPO = "https://github.com/fmount/autoreply"
SCRIPT_COMMAND = "autoreply"
SCRIPT_DESC = "A simple autoreply on private channels when away"
SCRIPT_HELPER = """
A simple autoreply plugin that replies on private channels when
the nick is away.
It can also be enabled only for a subset of servers and a filter
list can be built through the related config option.

- enabled: on || off
- time:    int() representing minutes
- msg:     The text that should be sent to the buffer
"""

DEFAULT_SERVERS_FILTER = ['bitlbee']

DEFAULT_SETTINGS = {
    'enabled': "on",
    'time': '1',
    'msg': "is away!",
    'mode': 'me',
    'server': DEFAULT_SERVERS_FILTER,
}

def get_nick(bufferp):
    '''
    Returns the nick on the current server, retrieved via bufferp query
    '''
    server = w.buffer_get_string(bufferp, "name").split(".")[0]
    nick = w.info_get("irc_nick", server)
    if DEBUG:
        w.prnt("", "[DEBUG] - The current Nick is %s on Server %s" % (nick, server))
    return nick, server

def do_command(bufferp, now, prefix, msg):
    '''
    This function implements the reply to the specified private buffer
    when time is expired
    params:
      now: from time.time() and represent the immediate present
      prefix: still not used, can be useful for future features
      msg: the default autoreply message

    '''
    before = w.buffer_get_string(bufferp, "localvar_timer")
    wait_for = int(DEFAULT_SETTINGS.get('time', 2))
    if w.config_get_plugin('time') != "":
        wait_for = w.config_get_plugin('time')
    if ((len(str(before)) == 0) or ((int(wait_for) * 60) <= (int(now) - int(str(before))))):
        if DEBUG:
            w.prnt("", "[DEBUG] - WAIT FOR %s" % w.config_get_plugin('time'))
            w.prnt("", "[DEBUG] - Last time found is: %s" % before)
            w.prnt("", "[DEBUG] - Sending text: %s" % msg)
            w.prnt("", "[DEBUG] - Setting time: %s" % str(int(now)))
            w.prnt("", "[DEBUG] - SERVERS: %s" % str(get_config_as_list((w.config_get_plugin('server')))))
        cmd = '/{} {}'.format(w.config_get_plugin('mode'), msg)
        w.command(bufferp, cmd)
        w.buffer_set(bufferp, "localvar_set_timer", str(int(now)))
    else:
        if DEBUG:
            w.prnt("", "[DEBUG] - No need to reply again (delta is %d)" % (int(now) - int(str(before))))
    return w.WEECHAT_RC_OK

def allowed_mode(m):
    if m is None or m == "":
        return False
    # note: only /me and /notice allowed for now
    amode = ['me', 'notice']
    return (True if m in amode else False)

def filter_server(s):
    '''
    True if the server should be filtered according to the
    defined SERVERS_FILTER list.
    '''
    slist = get_config_as_list(w.config_get_plugin('server'))
    if len(slist) == 0:
        slist = DEFAULT_SERVERS_FILTER  # using default plugin settings
    return (True if s in slist else False)

def config_as_str(value):
    """Convert config defaults to strings for weechat."""
    if isinstance(value, list):
        s = ''
        s = ','.join([v for v in value])
        return s
    else:
        return str(value)

def get_config_as_list(value):
    """Convert comma separated config strings to list"""
    if isinstance(value, list):
        return value
    return value.split(',')

def ar_catch_msg(data, bufferp, uber_empty, tagsn, isdisplayed, ishilight, prefix, message):

    # IRC PMs are caught by notify_private, but we need notify_message to
    # capture hilights in channels.
    if 'notify_private' not in tagsn:  # and not ishilight:
        return w.WEECHAT_RC_OK
    '''
    this function should react on receiving private messages, sending a reply using the
    established method (/notice vs /me vs other approaches) when the user is away but is
    still connected to the network using the weechat instance.
    '''

    # is the user away ?
    away = w.buffer_get_string(bufferp, "localvar_away")
    if (away == "" or w.config_get_plugin("only_away") == "on"):
        if DEBUG:
            w.prnt("", "[DEBUG] - Can't send the message while user (nick) is not AWAY")
        return w.WEECHAT_RC_OK

    # get local nick
    mynick, curr_serv = get_nick(bufferp)

    # update both the msg plugin setting and the DEFAULT_MSG
    if len(away) != "":
        DEFAULT_SETTINGS['msg'] = str(away)
        w.config_set_plugin('msg', str(away))

    # check if local nick is away
    if "on" in w.config_get_plugin('enabled') \
            and filter_server(curr_serv) \
            and allowed_mode(w.config_get_plugin('mode')):
        now = int(time.time())
        do_command(bufferp, now, prefix, DEFAULT_SETTINGS.get('msg', ''))
    return w.WEECHAT_RC_OK


if __name__ == "__main__" and IMPORT_OK:
    w.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", "")

    for option, value in DEFAULT_SETTINGS.items():
        if not w.config_is_set_plugin(option) and option not in DEFAULT_SETTINGS.get('msg', ''):
            w.config_set_plugin(option, config_as_str(value))

    # register commands and hooks
    w.hook_print("", "", "", 1, "ar_catch_msg", "")  # this hook helps catching private msgs
    w.hook_command(SCRIPT_COMMAND, SCRIPT_DESC, "[list|filter] | [on|off|toggle] | [time] | [text] | [server_name]", SCRIPT_HELPER, "", "auto_reply_cmd", "")
