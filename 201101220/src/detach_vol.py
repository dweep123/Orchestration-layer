import DelQueType
import create_vm
import resource_dis
import json
import rados, rbd 
import os
import libvirt
def json_out(out):
	  return json.dumps(out,indent=4)

def attach(server,arguments):
	volid=int(arguments)
	if volid in resource_dis.VOLUME_LIST:
		if volid in resource_dis.aord:
			if resource_dis.aord[volid]==0:
	       			server.wfile.write(json_out({"status":0}))
			else:
				vid=resource_dis.aord[volid]
				machid=resource_dis.virtMachine_info[vid][2]
				name=resource_dis.pm_id[machid]
				m_addr = name[0]+'@'+name[1]
				path = 'remote+ssh://'+m_addr+'/system'
				vm_na=resource_dis.virtMachine_info[vid][0]
				try:
					connect = libvirt.open(path)
					dom=connect.lookupByName(vm_na)
					f=open("/etc/ceph/ceph.conf",'r')
					l=f.readlines()
					l1=f.split("\n")
					host=l1[2].split('=')[1]
					f.close()
					xml="<disk type='network' device='disk'>   \
					     <source protocol='rbd' name='rbd/"+resource_dis.VOLUME_LIST[volid]+"'> \
					     <host name="+str(a)+" port='6789'/> \
	 				     </source> \
	 				     <target dev='hdb' bus='virtio'/>  \
					     </disk>"
					dom.detachDevice(xml)
					resource_dis.aord[volid]=0
					server.wfile.write(json_out({"status":1}))
				except:
					server.wfile.write(json_out({"status":0}))
		else:
			server.wfile.write(json_out({"status":0}))
	else:
		server.wfile.write(json_out({"status":0}))

