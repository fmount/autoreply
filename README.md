Autoreply weechat Plugin
---

Autoreply is a weechat script to automatically react on a private buffer whenever a message is received.
The goal is to keep weechat in foreground and set an automatic reply without closing the client.
Auto-replies are sent according to the *time* config option, and avoids to reply with the same message
if a bunch of messages are received.


## Options

Config options are created according to the following structure:

  SETTINGS = {
      'enabled': "on",
      'time': '1',
      'msg': "is away!",
      'mode': 'me',
      'server': SERVERS_FILTER,
  }

where SERVERS_FILTER is a server array where we want to to make the script working.
The default server array is bitlbee:


  SERVERS_FILTER = ['bitlbee']

but the options can be changed using the weechat /set command.

blabla

| Option | Description |
|---|---|
|**plugins.var.python.autoreply.enabled**| Enable/Disable the script|
|**plugins.var.python.autoreply.time** | The time it should wait before sending the msg again |
|**plugins.var.python.autoreply.msg**| The message sent on a private buffer (auto-reply msg) |
|**plugins.var.python.autoreply.mode** | The _mode_ used by weechat to send the message on the buffer (e.g., /me, /notice, etc)
|**plugins.var.python.autoreply.server** | a comma separated list of servers where the script can be enabled |


**Note**:

* At the moment the only (allowed) [modes are /me and /notice](https://github.com/fmount/autoreply/blob/master/autoreply.py*)
* If the server list is an empty array, the plugin rely on the [DEFAULT_SERVER_LIST](), represented by 'bitlbee' (and is hardcoded)
