import time
import json
def get_network(x):
#	recv = max([long(iface[4]) for iface in x['network'].values()])
	sent = max([long(iface[3]) for iface in x['network'].values()])
#	return min(recv, sent) / (1024*1024)
	return sent / (1024*1024)

def get_upload(x):
	sent = max([long(iface[3]) for iface in x['network'].values()])
	return sent / (1024*1024)

def get_download(x):
	recv = max([long(iface[4]) for iface in x['network'].values()])
	return recv / (1024*1024)

if __name__ == '__main__':
	with open('/root/plebmail.log', 'r') as f:
		data = f.readlines()[-100:]
	stats = [json.loads(line) for line in data]
	top = dict()
	for stat in stats:
		top[stat['name']] = stat
	top = list(top.values())
	top.sort(key=lambda x: get_network(x))
	content = "<thead><tr><th>DOWN</th><th>UP</th><th>NAME</th><th>IP</th><th>HOSTER</th><th>TIME</th></tr></thead>"
	content = content + "<tbody>"
	for i,t in enumerate(top[::-1]):
		update_time = int(time.time() - long(t['time']))
		content = content + '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>'.format(str(get_download(t)) + ' MB',str(get_upload(t)) + ' MB', t['name'], t['ip'], t['hoster'], str(update_time) + 's')
	content = content + "</tbody>"


	with open('/var/www/html/index.nginx-debian.html', 'w') as f:
		f.write('<html><head><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css" integrity="sha384-rwoIResjU2yc3z8GV/NPeZWAv56rSmLldC3R/AZzGRnGxQQKnKkoFVhFQhNUwEyJ" crossorigin="anonymous"></head><script type="text/javascript">var timeout = setTimeout("location.reload(true);",60000); function resetTimeout(){clearTimeout(timeout); timeout=setTimeout("location.reload(true);",60000);}</script><body style="background-color: #292b2c"><div class="container-fluid"><table class="table table-inverse" style="font-size: 34px; width: 100%">')
		f.write(content)
		f.write('</table></div></body></html>')
