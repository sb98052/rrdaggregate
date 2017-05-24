#!/usr/bin/python

import base64
import requests
import json
import os
import xmltodict
import pdb
import glob

def track(event, properties=None):
	if properties == None:
		properties = {}
	token = "2504af1a1d3eee3f1744a764807d89b0"
	if "token" not in properties:
		properties["token"] = token

	params = {"event": event, "properties": properties}
	data = base64.b64encode(json.dumps(params))
	request = "http://api.mixpanel.com/track/"
	result = requests.get(request,params={'data':data})
	return result

cdata = os.popen('/etc/rrdaggregate/rrdaggregate.py /etc/rrdaggregate/mp.yaml').read()
d = xmltodict.parse(cdata)
legend = d['xport']['meta']['legend']['entry']
data = d['xport']['data']['row'][-3]['v'] 
time = d['xport']['data']['row'][-3]['t'] 
pdata = []

for e in data:
	pdata.append(float(e))
  
if (len(legend)!=len(data)):
	'Mismatch between legend and data'
else:
	prop_list = zip(legend,pdata)
	props = dict(prop_list)
	slices = glob.glob('/vservers/*')
	slices = map(lambda s:s[10:],slices)
	props['hostname']=os.popen('hostname').read().rstrip()
	props['kernel']=os.popen('uname -r').read().rstrip()
	try:
		props['cpu']=100 - int(100*props['cpu']/12)/100.0;
		props['memory']/=(1024*1024)
	except:
		pass 
	props['ip']=os.popen('hostname -i').read().rstrip()
	props['slices']=slices
	
	try:
		last_sent = open('/tmp/lst_mp_hb').read()
	except:
		last_sent = '0'

	if (last_sent!=time):
		print 'Sending'
		track('heartbeat',props)
		open('/tmp/lst_mp_hb','w').write('%s'%time)
	
