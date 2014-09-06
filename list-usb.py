#! /usr/bin/python3

import os,re

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	DARK = '\033[97m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'


class GarminUConfigurator:
	keywords = []

	def __init__(self):
		self.keywords = ['garmin','mouse','intel']
		self.getDevices()
		self.guessUsbStorage()
		self.excludeNoStoDev()

	def getDevices(self):
		usblist = os.popen('lsusb').read().split('\n')[0:-1]
		keywords = self.keywords

		self.devices = []

		for x in usblist:
			#print match.group(0)
			data = re.search('([0-9a-f]{4}:[0-9a-f]{4})\s(.*)$',x).groups(1)
			data = list(data)
			data.append(x)
			if re.search('|'.join(keywords), data[1], flags=re.IGNORECASE):
				data.append(True)
			else:
				data.append(False)
			self.devices.append(data)

	def showDevices(self):
		devices = self.devices
		for idx,x in enumerate(devices):
			line = str(idx) + '. ' + x[1] 
			if x[-1]:
				print (bcolors.DARK + line + bcolors.ENDC)
			else:
				print (line)


	def getSerial(self,devId):
		lsusbvv = os.popen('lsusb -vv -d '+devId).read()

		iSerial=''
		for line in lsusbvv.split('\n'):
			match = re.search('iSerial(.*)',line)
			if match:
				iSerial = match.groups(1)[0]
		dSerial = ''
		if iSerial != '':
			match = re.search('(.*)\s(.*)',iSerial)
			if match:
				dSerial = match.groups(1)[1]
		self.iSerial = dSerial
		return dSerial

	def userSelect(self):
		selected = ''
		def checkLimit(s):
			if type(selected) is str:
				print('input the integer 0 to '+str(len(self.devices)-1))
				return True
			if type(selected) is int:
				if selected <  len(self.devices):
					return False
				print('out of range')
			return True

		while checkLimit(selected):
			try:
				selected = input('Choice your device: ')
				selected = int(selected)
			except ValueError:
				pass
		self.selected = selected
		self.devId = self.devices[int(self.selected)][0]
		return selected

	def askIfOk(self):
		surestr = "no serial found (it means it is not a GPS device?), are you sciur (write 'yes' exactly if so)? "
		sure = 'n' 
		sure = input(surestr)
		match = re.match('yes',sure)
		if match:
			 return True
		return False

	def selectDev(self):
		isKo = True
		while isKo:
			self.showDevices()
			self.userSelect()
			self.getSerial(self.devId)
			print ('seriaLL',self.iSerial)
			if not self.iSerial:
				isKo = not self.askIfOk()
			else:
				isKo = False
		print(self.selected,self.iSerial);

	def getSelectedVendProd(self):
		return self.devId

	def parseMountedDev(self):
		mountcmd = os.popen('mount').read().split('\n')
		self.mountedDev = []
		for x in mountcmd:
			match = re.match('(/dev/.*)\s.*\s(/[^\s]*)(.*)',x)
			if match:
				l = match.groups(1)
				self.mountedDev.append(list(l))

	def guessUsbStorage(self):
		blocks = os.popen('ls -l /sys/block').read().split('\n')[1:-1]
		self.guesdUsb = []
		for line in blocks:
			x = re.split('\s+',line)
			match = re.search('/usb',x[10])
			if match:
				self.guesdUsb.append( [x[8],x[10]] )

	def getVendorProduct(self,path):
		idx = path.index('usb')
		p = path[0:idx] + '/'.join(path[idx:].split('/')[:3])
		print (p)
		return '091e:2464'

	def excludeNoStoDev(self):
		acceptableVp = []
		for x in self.guesdUsb:
			path = x[1]
			iViP = self.getVendorProduct(x[1])
			acceptableVp.append(iViP)
		newDevices = []
		for x in self.devices:
			if x[0] in acceptableVp:
				newDevices.append(x)
		self.devices = newDevices

GC = GarminUConfigurator()
GC.selectDev()
print(GC.getSelectedVendProd())
GC.parseMountedDev()
print(GC.mountedDev)
print (GC.guessUsbStorage())
print( GC.guesdUsb)
#print devices
