import sys
import os
sys.path.append(os.path.abspath('../tracker'))
import tracker_bot as tbot
import pandas as pd

from flask import Flask, render_template

import json
import time
from datetime import datetime

app = Flask(__name__)

# ==============================================================================
# Initial static data parsing from file
# ==============================================================================
data_path = "~/.config/"
data_name = "tracker.data"
data_file = os.path.join(data_path, data_name)

cols = ['timestamp', 'nick', 'type', 'value']
data = pd.read_csv(data_file,
                   skipinitialspace=True,
                   delimiter=';',
                   error_bad_lines=False,
                   names=cols,
                   parse_dates=[0])

# remove null values
data = data.dropna(subset=['value'])
data = data[pd.to_numeric(data['value'], errors='coerce').notnull()]
data.value = data.value.astype(float)

units = {
    'MB_balance' : 'MBs',
    'downloaded' : 'MBs',
    'uploaded' : 'MBs',
    'matchmakers' : 'peers',
}

u_nicks = data.nick.unique().tolist()

# main data storage for graph
u_nicks_data = {}
for n in u_nicks:
    u_nicks_data[n] = {}
    for k in units.keys():
        dt = data.loc[(data['nick']==n) & (data['type']==k)]
        df = dt.filter(items=['timestamp', 'value'])
        df.columns=['x', 'y']
        df.x = df.x.astype(str)
        u_nicks_data[n][k] = df.to_dict('records')


# nodes = [{'id': n, 'label': n, 'group':u_nicks.index(n)} for n in u_nicks]
# edges = []

# _data_network = {'nodes':nodes, 'edges': edges}

# ==============================================================================
# Dynamic data parsing
# new data is stored in memory as tree
# ==============================================================================

class BotNode:

    info_type = ['dead', 'nick', 'exitnode', 'host', 'vpn', 'children']

    def __init__(self, id):
        self.id = id
        self.dead = True
        self.nick = 'unknown'+str(time.time())[:-3]
        self.exitnode = 'unknown'
        self.host = 'unknown'
        self.vpn = 'unknown'
        self.last_seen = time.time()
        self.children = {}

    def set_status(self, nickname=None, exitnode=None, host=None, vpn=None, last_seen=None, dead=True):
        self.nick = nickname or self.nick
        self.dead = dead
        self.last_seen = last_seen or self.last_seen
        self.exitnode = exitnode or self.exitnode
        self.host = host or self.host
        self.vpn = vpn or self.vpn

    def add_child(self, tree):
        root = tree.pop(0)
        child_id = root 
        cur_child = self
        while tree:
            child_id += '.'+tree.pop(0)
            if child_id not in cur_child.children.keys():
                child = BotNode(child_id)
                cur_child.children[child_id] = child 
            else:
                child = cur_child.children[child_id]

            cur_child = child
        return cur_child
                
    def get_children(self):
        visited = []
        child_queue = list(self.children.values())
        while child_queue:
            child = child_queue.pop(0)
            if child not in visited:
                visited.append(child)
            for gchild in child.children.values():
                if gchild not in visited:
                    child_queue.append(gchild)
                    visited.append(gchild)
        return visited

    def get_nodes(self):
        all_children = self.get_children()
        nodes = []
        nodes.append({"id": self.nick, "label": "%s (%s)"%(self.nick, self.get_group()), "group": self.get_group()})
        for c in all_children:
            nodes.append({"id": c.nick, "label": "%s (%s)"%(c.nick, c.get_group()), "group": c.get_group()})
        return nodes

    def get_edges(self):
        visited = []
        edges = []
        child_queue = list(self.children.values())
        cur = self
        while child_queue:
            child = child_queue.pop(0)
            if child not in visited:
                visited.append(child)
                edges.append({"from":cur.nick, "to": child.nick})
                cur = child
            for gchild in child.children.values():
                if gchild not in visited:
                    child_queue.append(gchild)
        return edges

    def get_group(self):
        if self.dead:
            group = 'dead'
        elif self.host.lower() == 'linevast':
            group = 'linevast'
        elif self.host.lower() == 'blueangelhost':
            group = 'blueangelhost'
        elif self.host.lower() == 'twosync':
            group = 'twosync'
        elif self.host.lower() == 'proxhost':
            group = 'proxhost'
        elif self.host.lower() == 'unknown':
            group = 'unknown'
        elif self.host.lower() == 'undergroundprivate':
            group = 'undergroundprivate'
        else:
            group = 'unknown'
        return group

    def get_info(self):
        return {
            "id": self.id,
            "children": len(self.children.values()),
            "nick": self.nick,
            "dead": self.dead,
            "host": self.host,
            "exitnode": self.exitnode,
            "vpn": self.vpn
        }

    def __str__(self): 
        return "id: %s \
        \n children: %s \
        \n dead: %s \
        \n nick %s \
        \n host %s \
        \n exitnode %s \
        \n vpn %s" % (self.id,
        self.children,
        self.dead,
        self.nick,
        self.host,
        self.exitnode,
        self.vpn)


root_bot_nodes = {} #id=tree, bot
bot_node_by_nicks = {}

def handle_data(bot_nick, key, value):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
   
    if key == 'general':

        # reset dead state to DEAD until message is received
        for stored_bot in root_bot_nodes.values():
            if (time.time() - stored_bot.last_seen) > 1800.0:
                stored_bot.set_status(dead=True)

        value = ' '.join(value)
        jd = value.replace("u\'", "\'").replace("True", "\'True\'").replace("False", "\'False\'").replace("\'", "\"")
        d = json.loads(jd)

        tree = d['tree'].split('.')
        root = tree[0]
        if root not in root_bot_nodes.keys():
            root_bot = BotNode(root)
            root_bot_nodes[root] = root_bot

            # nice little mapping from irc nick to BotNode
            # it's a chaos driven design pattern
            # the real way to do all of this is to use the tree received from IRC as id everywhere.
            bot_node_by_nicks[root] = root_bot                    

        root_bot = root_bot_nodes[root]
     
        if len(tree) == 1:
            print "bot %s is root" % bot_nick
            root_bot.set_status(bot_nick, d['exitnode'], d['host'], d['vpn'], last_seen=time.time(), dead=False)
        else:
            print "add %s to: %s" %('.'.join(tree), root)
            child = root_bot.add_child(tree)
            child.set_status(bot_nick, d['exitnode'], d['host'], d['vpn'], last_seen=time.time(), dead=False)
            bot_node_by_nicks[bot_nick] = child

    else:
        if bot_nick not in u_nicks_data.keys():
            u_nicks_data[bot_nick] = {}

        if key not in u_nicks_data[bot_nick].keys():
            u_nicks_data[bot_nick][key] = []

        if bot_nick not in root_bot_nodes.keys():
            root_bot = BotNode(bot_nick)
            root_bot.set_status(nickname=bot_nick, last_seen=time.time(), dead=False)
        
        u_nicks_data[bot_nick][key].append({'x': current_time, 'y': value})


tracker = tbot.TrackerBot('watcher', handle_data)

@app.route('/')
def root():
    return render_template('index.html', data=units.keys())

@app.route('/network')
def network():
    _data_network = {"nodes":[], "edges":[]}
    for bot in root_bot_nodes.values():
        _data_network["nodes"] += bot.get_nodes()
        _data_network["edges"] += bot.get_edges()
    _data_network["nodes"] = {v["id"]:v for v in _data_network["nodes"]}.values()
    return json.dumps(_data_network)

@app.route('/node/<id>/<type>')
def node(id, type):
    if type in units.keys():
        return json.dumps(u_nicks_data[id][type])
    elif type == 'info':
        return json.dumps(bot_node_by_nicks[id].get_info())

@app.route('/shownodes')
def show_nodes():
    nodes = []
    for bot in root_bot_nodes.values():
        nodes.append(str(bot))
    return str(nodes)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500)
