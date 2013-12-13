#!/bin/python
import BaseHTTPServer
import sys
from SocketServer import ThreadingMixIn
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import DelQueType
import create_vm
import resource_dis
import json
import rados, rbd
import os
HandlerClass = SimpleHTTPRequestHandler
ServerClass  = BaseHTTPServer.HTTPServer
PORT_NUMBER = 80
POOL_NAME="rbd"
HOST_NAME='chitra-HP-Pavilion-g6-Notebook-PC' #todo
radosConn=rados.Rados(conffile='/etc/ceph/ceph.conf')
radosConn.connect()
POOL_NAME="rbd"
if POOL_NAME not in radosConn.list_pools():
	radosConn.create_pool(POOL_NAME)
ioctx = radosConn.open_ioctx(POOL_NAME)
rbdInstance = rbd.RBD()
VOLUME_LIST={}
def json_out(out):
	  return json.dumps(out,indent=4)
class My_handler(BaseHTTPRequestHandler):
	def do_GET(self):
		print self.path
		url=self.path
		if '/vm/create' in url:
			whattodo = url
			arguments = []
			arg_split = url.split('?')[1].split('&')
			for i in xrange(0,3):
				arguments.append((arg_split[i].split('='))[1])
			print arguments
			create_vm.create(self,arguments)
		elif '/vm/destroy' in url:
			print url.split('?')[1].split('=')[1]
			DelQueType.destroy(self,url.split('?')[1].split('=')[1])
		elif '/vm/query' in url:
			DelQueType.query(self,url.split('?')[1].split('=')[1])
		elif '/vm/types' in url:
			DelQueType.vmtypes(self)
		elif '/vm/image/list' in url:
			fn=resource_dis.image_id
			l=[]
			for x in fn:
				d={}
				d["id"]=x
				d["name"]=fn[x][2][0]
				l.append(d)
			p={}
			p["iamges"]=l
			self.wfile.write(json_out(p))
		elif '/volume/create' in url:
			global VOLUME_LIST
			url=self.path
			arg=self.path.split('?')
			volume_name = arg[1].split('&')[0].split('=')[1]
			volume_size = arg[1].split('&')[1].split('=')[1]
			actual_size = int(float(volume_size)*(1024**2))
			global rbdInstance
			rbdInstance.create(ioctx,str(volume_name),actual_size)
			os.system('sudo rbd map %s --pool %s --name client.admin'%(str(volume_name),str(POOL_NAME)));
			volume_id=len(VOLUME_LIST)
			VOLUME_LIST[int(volume_id)]=str(volume_name)
			print VOLUME_LIST
			self.wfile.write(json_out({"volumeid":volume_id}))

		elif '/volume/destroy' in url:
			global VOLUME_LIST
			global rbdInstance
			print VOLUME_LIST
			url=self.path
			arg=url.split('?')
			volume_id = int(arg[1].split('=')[1])
			if volume_id in VOLUME_LIST:
				volume_name=str(VOLUME_LIST[int(volume_id)])
				os.system('sudo rbd unmap /dev/rbd/%s/%s'%(POOL_NAME,volume_name))
				rbdInstance.remove(ioctx,volume_name)
				del VOLUME_LIST[int(volume_id)]
				self.wfile.write(json_out({"status":1}))
			else:
				print "here\n"
				self.wfile.write(json_out({"status":0}))
		else:
			self.send_error(404,"File Not Found")
def main():
	
	pm = sys.argv[1]
	image_file = sys.argv[2]
	vm_type = sys.argv[3]

	resource_dis.mach(pm)
	resource_dis.imagefile(image_file)
	resource_dis.VMTYPES(vm_type)
#	PORT_NUMBER = int(sys.argv[1])
	server_address = ('', PORT_NUMBER)
	httpd = ServerClass(server_address, My_handler)
	print "Server Started at port", PORT_NUMBER
	httpd.serve_forever()



if __name__ == "__main__":
	main()
