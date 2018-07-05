import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import random

import warnings
warnings.filterwarnings('ignore')

# inspiration for improvements can be found here:
# http://www.djmannion.net/psych_programming/data/inferential/inferential.html
# https://blog.modeanalytics.com/python-data-visualization-libraries/


#########################################
## Initialize the data                 ##
#########################################

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
# set index col properly
data = data.set_index('timestamp')
# restore faults
data.type[data.type == 'BM_balance'] = 'MB_balance'

units = {
    'MB_balance' : 'MBs',
    'downloaded' : 'MBs',
    'uploaded' : 'MBs',
    'matchmakers' : 'matchmakers'
}

#########################################
## more prepping                       ##
#########################################
nickss = data.nick.unique().tolist()
colors = []
def random_color():
    return random.random()*0.5+0.5
for nick in nickss:
    colors.append((random_color(),random_color(),random_color()))
plt_types = ['-','--',':','-.']


#########################################
## The plot methods                    ##
#########################################
def plot(*dfs, **other):
    #####################
    ## THE MAIN PLOT   ##
    #####################

    plt.figure()

    titel = dfs[0].type.iloc[0] if not 'titel' in other else other['titel']
    max_value = 0
    ylabel = None
    for i in range(len(dfs)):
        df = dfs[i]
        nicks = df.nick.unique()
        max_value = max(max_value, 1.4 * max(df.value))
        data_type = dfs[0].type.iloc[0]
        line_type = plt_types[i]

        for nick in nicks:
            label = df.type.iloc[0] + " " + nick
            color = colors[nickss.index(nick)]
            df.value[df.nick == nick].plot(label=label, c=color, linestyle=line_type)

        if (data_type in units) and (ylabel is None):
            ylabel = units[data_type]

    plt.title('Values for %s' % titel)
    plt.ylabel(ylabel)
    plt.xlabel('Dates')
    plt.ylim(0, max_value)
    plt.legend()
    plt.savefig("FIG__Values_for_" + titel)

    #####################
    ## THE DIFFERENCES ##
    #####################

    if 'dif' in other and other['dif']:

        plt.figure()

        ylabel = None

        for i in range(len(dfs)):
            df = dfs[i]
            data_type = dfs[0].type.iloc[0]

            if (data_type in units) and (ylabel is None):
                ylabel = units[data_type]

            line_type = plt_types[i]
            for nick in nicks:
                delta = df[df.nick == nick].value.diff()
                label = df.type.iloc[0] + " " + nick
                color = colors[nickss.index(nick)]
                delta.plot(label=label, c=color, linestyle=line_type)

        plt.title('Delta %s' % titel)
        plt.ylabel(ylabel)
        plt.xlabel('Dates')
        plt.legend()
        plt.savefig("FIG__Deltas_for_" + titel)

    #####################
    ## FINALIZE        ##
    #####################

    plt.show()


#########################################
## Create the plots                    ##
#########################################
uploaded = data[data.type=='uploaded']
downloaded = data[data.type=='downloaded']
MB = data[data.type=='MB_balance']
matchmakers = data[data.type=='matchmakers']

plot(uploaded, downloaded, dif=True)
plot(MB, dif=True)
plot(matchmakers)
