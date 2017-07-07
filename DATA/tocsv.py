import sys
import json

if __name__ == '__main__':
	name = args = sys.argv[1]
	
	with open(name, 'r') as f:
		data = f.readlines()
	stats = [json.loads(line) for line in data]
	with open('{0}.csv'.format(name), 'w') as f:
		f.write('ip,time,hoster,name,recv,sent,ram,ram_ava,MC_offer,BTC_offer,cores,cpu\n')
		for s in stats:
			netio = s['network']
			recv = max([long(iface[4]) for iface in netio.values()])
			sent = max([long(iface[3]) for iface in netio.values()])
			cpu_use = sum([float(c) for c in s['cpu']])
			btc = s['last_offer']['BTC'] if 'BTC' in s['last_offer'].keys() else s['last_offer']['BTC:']
			f.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n'.format(
				s['ip'],
				s['time'],
				s['hoster'],
				s['name'],
				recv,
				sent,
				s['ram'][0],
				s['ram'][1],
				s['last_offer']['MC'],
				btc,
				len(s['cpu']),
				cpu_use
			))

