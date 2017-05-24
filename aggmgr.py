import yaml
import os
import re

FIND_PATH='find'

class AggManager:
	def __init__(self, program):
		self.parsed = yaml.load(open(program))['entries']
		self.props = {}

		self.matches = {}
		for e in self.parsed:
			e['compiled_regex'] = re.compile(r'%s'%e['regex'])
			self.props[e['name']] = e
			self.matches[e['name']]={}
	
	def match_on_file(self, f):
		for e in self.parsed:
			r = e['compiled_regex']
			m = re.match(r, f)
			if m:
				key_path = [e['name']] + list(m.groups())
				key = '###'.join(key_path)
				try:
					self.matches[e['name']][key].append(f)
				except KeyError:
					self.matches[e['name']][key]=[f]

	def match_on_directory(self, dirname):
		cmdline = '%s %s -printf "%%P\n"'%(FIND_PATH, dirname)
		files = [line.rstrip() for line in os.popen(cmdline)]

		for f in files:
			self.match_on_file(f)

	def gen_defs(self):
		i0 = 0
		i1 = 0
		self.defs = []
		self.cdefs = []
		self.xports = []
		for e in self.parsed:
			n = e['name']
			psexp = []
			
			for k,l in self.matches[n].items():
				xvar='x%d'%i1
				for v in l:
					svar='s%d'%i0
					ds = self.props[n]['ds']
					try:
						print self.props[n]['step']	
					except:
						pass

					try:
						step = ':step=%r'%self.props[n]['step']
					except:
						step = ''
				
					try:
						cf = self.props[n]['cf']
					except:
						cf = 'AVERAGE'

					self.defs.append('DEF:%s=%s:%s:%s%s'%(svar,v,ds,cf,step))
					if (psexp):
						psexp.extend([svar,'ADDNAN'])
					else:
						psexp=[svar]
					i0+=1

				self.cdefs.append('CDEF:%s=%s'%(xvar,','.join(psexp)))
				i1+=1
				self.xports.append('XPORT:%s:"%s"'%(xvar,k))
