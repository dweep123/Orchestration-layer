#!/bin/python
import libvirt 
import json
import resource_dis
import subprocess
import os
def json_out(out):
	return json.dumps(out,indent=4)
def get_pm(ins_type,h):
	print "This Vm has to be created ",ins_type
	totalpms=resource_dis.tpms
	current_pmid=resource_dis.c_pmid
	print totalpms,current_pmid
	tocheck=current_pmid
	current_pmid+=1
	if current_pmid > totalpms:
		current_pmid=1000
	print "starting form here" , current_pmid
	while 1:
		if current_pmid > totalpms:
			current_pmid=1000
		if resource_dis.pm_freespace[current_pmid][0] >= ins_type[2] and resource_dis.pm_freespace[current_pmid][1] >= ins_type[3] and resource_dis.pm_freespace[current_pmid][2] >= ins_type[1] and resource_dis.pm_freespace[current_pmid][3]>=h:
# resource_dis.pm_freespace[current_pmid][0]-= ins_type[2] 
#			 resource_dis.pm_freespace[current_pmid][1]-= ins_type[3]
#			 resource_dis.pm_freespace[current_pmid][2]-= ins_type[1]
			 print "This machine has been selected to created VM ", resource_dis.pm_id[current_pmid],current_pmid
			 resource_dis.c_pmid=current_pmid
			 return resource_dis.pm_id[current_pmid],current_pmid
		if current_pmid==tocheck:
			 resource_dis.c_pmid=current_pmid
			 break
		current_pmid+=1
	return 0,0


# 		xml = create_xml(im_loc,emulator_path,emulator1,arch_type,virm_name,specification[3],specification[2]) 

#def create_xml(loc,a,name,type_p):
def create_xml(im_loc,emulator_path,emulator1,arch_type,name,cpu,ram):
	xml = "<domain type="+str(emulator1)+  		\
			"><name>" + name + "</name>				\
			<memory >"+str((ram *100000)/1024)+"</memory>					\
			<vcpu>"+str(cpu)+"</vcpu>						\
			<os>							\
			<type arch='"+arch_type+"' machine='pc'>hvm</type>		\
			<boot dev='hd'/>					\
			</os>							\
			<features>						\
			<acpi/>							\
			<apic/>							\
			<pae/>							\
			</features>						\
			<on_poweroff>destroy</on_poweroff>			\
			<on_reboot>restart</on_reboot>				\
			<on_crash>restart</on_crash>				\
			<devices>							\
			<emulator>"+str(emulator_path)+"</emulator>	\
			<disk type='file' device='disk'>			\
			<driver name="+str(emulator1)+" type='raw'/>			\
	<source file='"+str(im_loc)+"'/>                      \
			<target dev='hda' bus='ide'/>				\
			<address type='drive' controller='0' bus='0' unit='0'/>	\
			</disk>							\
			</devices>						\
			</domain>"
	return xml	
	
def create(server,arguments):
		resource_dis.server_header(server,arguments)
		virm_name = str(arguments[0])		
		virm_type = int(arguments[1])		
		image_type = int(arguments[2])	
		specification = resource_dis.virm_types[virm_type-1]
		if "_64" in  resource_dis.image_id[image_type][2][0]:
			h=64
		else:
			h=32
		mach,machid=get_pm(specification,h)
		print virm_type
		print image_type
		print specification
		if machid == 0:
			print " Sorry No machines meet the requirements"
			return
		m_addr = mach[0]+'@'+mach[1] #is machine pe vm create karna hai!!
		path = 'remote+ssh://'+m_addr+'/system'
		images_list = resource_dis.image_id[image_type] 
		image_machine = images_list[0][0]+'@'+images_list[0][1]
		path_image = images_list[1]			#Find the location of image
		if not os.path.isfile('./'+images_list[2][0]):
			print m_addr,path_image
			subprocess.call(["scp",':'.join([image_machine,path_image]),'.'])
		try:
			subprocess.call(["scp", './'+images_list[2][0],':'.join([m_addr,'/home/'+mach[0]])])
		except:
			print "Image is already there!! No need to copy then!!"

		if machid == 0:
			print " Sorry No machines meet the requirements"
			return
		m_addr = mach[0]+'@'+mach[1]
		path = 'remote+ssh://'+m_addr+'/system'
		try:
			connection = libvirt.open(path)
		except:
			print "Could Not Open Connection\n"
			return
		im_loc='/home/'+mach[0]+'/'+images_list[2][0]
		machine_info = connection.getInfo()
		machine_spe = connection.getCapabilities()	
		emulator_path = machine_spe.split("emulator>")
		emulator_path = emulator_path[1].split("<")[0]	#location of xen/qemu
		emulator1 = machine_spe.split("<domain type=")
		emulator1 = emulator1[1].split(">")[0]		#emulator present xen/qemu
		arch_type = machine_spe.split("<arch>")
		arch_type = arch_type[1].split("<")[0]
 		xml = create_xml(im_loc,emulator_path,emulator1,arch_type,virm_name,specification[3],specification[2]) 
		print 
		print " so here printing xml", xml
		print
		connect_xml = connection.defineXML(xml)
		try:
			connect_xml.create()
			print "VM SUCCESSFULLY CREATED!! :)" 
			vmid = resource_dis.assignVMid(machid)	
			resource_dis.virtMachine_info[vmid] = [virm_name, specification, machid,virm_type]
			server.wfile.write(json_out({"vmid":vmid}))		
			#server.wfile.write(" { \n vmid: %d \n }" % vmid)
			resource_dis.pm_freespace[machid][0]-= specification[2] 
			resource_dis.pm_freespace[machid][1]-= specification[3]
			resource_dis.pm_freespace[machid][2]-= specification[1]
		except Exception,e:
			print str(e)
			server.wfile.write(json_out({"vmid":0}))	
			#server.wfile.write(" { \n vmid: 0 \n }" )
