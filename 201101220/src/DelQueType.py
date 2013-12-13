#!/bin/python
import resource_dis 
import libvirt
import json
def json_out(out):
		return json.dumps(out,indent=4)
def destroy(server,attributes):
	resource_dis.server_header(server,attributes)
	try:
		vmid = int(attributes)
		print "Deleting VM with vmid",vmid
		pm_machine = resource_dis.pm_id[resource_dis.virtMachine_info[vmid][2]]
		pm_addr = pm_machine[0]+'@'+pm_machine[1]
		path = 'remote+ssh://'+pm_addr+'/system'
		print " ssh to virtual machine location",path
		virm_name = resource_dis.virtMachine_info[vmid][0]
		connection = libvirt.open(path)
		try:
			r = connection.lookupByName(virm_name)
		except:
			print "The said virtual machine does not exist on any physical machine."
		if r.isActive():
			r.destroy()
		r.undefine()
		vmtype=resource_dis.virtMachine_info[vmid][1]
		print " This VM is to be deleted",vmtype
#disk=vmtype[1]
#		ram =vmtype[2]
#		cpu=vmtype[3]
		pmid = resource_dis.virtMachine_info[vmid][2]
		resource_dis.pm_freespace[pmid][0]+=vmtype[2]
		resource_dis.pm_freespace[pmid][1]+=vmtype[3]
		resource_dis.pm_freespace[pmid][2]+=vmtype[1]
		del resource_dis.virtMachine_info[vmid]

		print "Virtual machine deleted and domain undefined."
		print "Finally resources of machine are " ,resource_dis.pm_freespace[pmid]
		server.wfile.write(json_out({"status":1}))
	#	server.wfile.write(fileHandling.json_out({"vmid":vmid}))	
	#	server.wfile.write('{ \n status :1 \n }')
	except:
		server.wfile.write(json_out({"status":0}))
#		server.wfile.write('{ \n status : 0 \n }')



def query(server,attributes):
	resource_dis.server_header(server,attributes)
	try:
		vmid = int(attributes)
		print "Details of virtual machine with id",vmid
		instype = resource_dis.virtMachine_info[vmid][3]
		virm_name = resource_dis.virtMachine_info[vmid][0]
		pm_id = resource_dis.virtMachine_info[vmid][2]
		print "{vmid:",vmid,", name: ",virm_name,"instance_type: ",instype,"pmid: ",pm_id
		server.wfile.write(json_out({"vmid":vmid, "name":virm_name, "instance_type": instype, "pmid": pm_id}))
	except Exception,e:
		print str(e)
		server.wfile.write(json_out({"status":0}))

def vol_query(server,arg):
	if int(arg) in resource_dis.VOLUME_LIST:
		if int(arg) in resource_dis.aord:
			if resource_dis.aord[int(arg)]==0:
				server.wfile.write(json_out({"volumeid":arg, "name":resource_dis.VOLUME_LIST[int(arg)],"size":resource_dis.vol_size[int(arg)], "status":"available"}))
			else:
				server.wfile.write(json_out({"volumeid":arg, "name":resource_dis.VOLUME_LIST[int(arg)],"size":resource_dis.vol_size[int(arg)], "status":"attached" , "vmid":resource_dis.aord[int(arg)]}))
		else:
				server.wfile.write(json_out({"error":"given volume id does not exist"}))

	else:
		server.wfile.write(json_out({"error":"given volume id does not exist"}))


				
			
				

		
		
def vmtypes(server):
	resource_dis.server_header(server,200)
	try:
		f = resource_dis.file_type
		fopen = open(f)
		server.wfile.write(json_out(json.load(fopen)))
	except Exception,e:
		print str(e)
		server.wfile.write(json_out({"status":0}))
