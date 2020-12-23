#!/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2017 Maarten de Vries <maarten@de-vri.es>
#
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

#
# Autosort automatically keeps your buffers sorted and grouped by server.
# You can define your own sorting rules. See /help autosort for more details.
#
# https://github.com/fmount/autoreply
#

#
# Changelog:
# 0.1:
#

from __future__ import print_function
from prettytable import PrettyTable
import time

IMPORT_OK = True

try:
    import weechat as w
except ImportError:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: http://www.weechat.org/")
    IMPORT_OK = False

"""
TODO: A description of the plugin
"""

SCRIPT_NAME = "autoreply"
SCRIPT_AUTHOR = "Francesco Pantano <fmount@inventati.org>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Simple autoreply on private channels when away"
SCRIPT_REPO = "https://github.com/fmount/autoreply"
SCRIPT_COMMAND = "autoreply"
SCRIPT_DESC = "A simple autoreply on private channels when away"
SCRIPT_HELPER = """
TODO: Description of the plugin and available options

- enabled: on || off
- time:    int() representing minutes
- msg:     The text that should be sent to the buffer
"""

DEFAULT_SETTINGS = {
    'enabled': "off",
    'time': 2,
    'msg': "is away"
}

class AutoReplyConfig():
    ''' The autoreply configuration. '''

    def __init__(self, *args):
        self.enabled = "off"
        self.time = 2
        self.msg = ""

    def print_config(self):
        x = PrettyTable()
        x.field_names = ["AutoReply Status", "Repeat Time", "Message"]
        x.addRow([self.enabled, self.time, self.msg])
        # print should happen within the weechat context
        w.prnt("", x)

def reload_config():
    ##config.reload()
    pass

def auto_reply_cmd():
    pass

def get_nick(bufferp):
    '''
    Returns the nick on the current server, retrieved via bufferp query
    '''
    server = w.buffer_get_string(bufferp, "name").split(".")[0]
    nick = w.info_get("irc_nick", server)
    return nick

def is_away(local_nick):
    pass

def reply(now):
    '''
    This function implements the reply to the specified private buffer
    if timer is expired
    params:
      now: it comes from time.time() and represent the immediate present
    '''
    last = w.buffer_get_string(bufferp, "localvar_btime")
    if last == "" or (DEFAULT_SETTINGS.get('time', 2) * 60 <= (int(now) - int(last))):
        w.command()  # I can send the reply on the buffer
        w.buffer_set_string(bufferp, "localvar_btime", str(int(time.time())))
    else:
        w.buffer_set_string(bufferp, "localvar_btime", str(int(time.time())))
    return w.WEECHAT_RC_OK



def ar_catch_msg(data, bufferp, uber_empty, tagsn, isdisplayed, ishilight, prefix, message):

    # IRC PMs are caught by notify_private, but we need notify_message to
    # capture hilights in channels.
    #if 'notify_private' in tagsn and not ishilight:
    #    return weechat.WEECHAT_RC_OK
    '''
    this function should react on receiving private messages, sending a reply using the
    established method (/notice vs /me vs other approaches) when the user is away but is
    still connected to the network using the weechat instance.
    '''

    # are the user away?
    away = w.buffer_get_string(bufferp, "localvar_away")
    if (away == "" and w.config_get_plugin("only_away") == "on"):
        return w.WEECHAT_RC_OK

    # get local nick
    mynick = get_nick(bufferp)
    # check if local nick is away
    if is_away(mynick) and "on" in DEFAULT_SETTINGS.get('enabled', "off"):
        # TODO: I should be able to reply if timer is ok with that!
        reply(time.time())

def ar_config_change():
    pass


if __name__ == "__main__" and IMPORT_OK:
    w.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", "")

    #config = AutoReplyConfig(DEFAULT_SETTINGS)

    for option, value in DEFAULT_SETTINGS.items():
        if not w.config_is_set_plugin(option):
            w.config_set_plugin(option, value[0])

    # register commands and hooks
    w.hook_print("", "", 1, "ar_catch_msg", "")  # this hook helps catching private msgs
    w.hook_config("plugins.var.python." + SCRIPT_NAME + ".*", "ar_config_change", "")  # be notified about config changes
    w.hook_command(SCRIPT_COMMAND, SCRIPT_DESC, "[list] | [on|off|toggle] | [time] | [text]", SCRIPT_HELPER, "", "auto_reply_cmd", "")
