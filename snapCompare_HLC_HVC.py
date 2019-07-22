import os
import re
import math
import sys
#from sys import exit

print("Number of arguments: "+str(len(sys.argv)))
debug_mode = False
if sys.argv[1] == "1":
	debug_mode = True
	print("Debug mode.")
else:
	print("Non-debug mode.")

#using r to specify that raw string is used... if you don't want to use r use double backslash for every backslash in the path
#do not forget to specify the file extension
hlc_snapshot_file_loc = r'C:\Users\user1\Documents\TraceToReporting_HLC_BasedDetection\predicate_a0.010000_e100_l0.100000_d10_v1_run0\snapshots_counted_clkHLC_mode0.txt'
hvc_snapshot_file_loc = r'C:\Users\user1\Documents\TraceToReporting_HLC_BasedDetection\predicate_a0.010000_e100_l0.100000_d10_v1_run0\snapshots_hvc_msgmode0.txt'


#not sure if epsilon is required but leaving old code as it is
epssearch = re.search('_e(\d+)_l', hlc_snapshot_file_loc)
if epssearch:
	epsilon=int(epssearch.group(1)); #get the current epsilon value to print at the end
	print('Epsilon:'+str(epsilon)+'\n')

fpv=0
tpv=0
total_hlc_snapshots=0
#for each snapshot in the HLC-snapshot file of the format [P8:<102,<102,0>> --> [P8:<z,
	#search the HVC-snapshot file for a line containing [P8 and <pt:x - y> s.t. x <= z and z <=y
		#if exists -> then increment true positive
		#else increment false positive

#since contents of the file have increasing timestamps we do not have to read from the beginning of the file for each search
# we can continue from the location we stopped at the end of the previous search

hlc_snapshot_file = open(hlc_snapshot_file_loc, 'r')
hvc_snapshot_file = open(hvc_snapshot_file_loc, 'r')
line = hlc_snapshot_file.readline()
#read a line and pick the pt + process value
while line:
#{
	m1 = re.search('\[P(\d+):\<(\d+)\,', line)
	if m1:
	#{
		process_id=int(m1.group(1));
		hlc_pt = int(m1.group(2));
		if debug_mode:
			print("hlc:"+line);
		hvc_line = hvc_snapshot_file.readline()
		total_hlc_snapshots = total_hlc_snapshots +1 
		while hvc_line:
		#{
			search_process = '\[P'+str(process_id)
			if debug_mode:
				print("hvc line:"+hvc_line +"looking for"+search_process);
			#[P1:<0,1,0,0,0,0,0,0,0,0,> - <0,2,0,0,0,0,0,0,0,0,><pt:101 - 102>]
			m2 = re.search(search_process, hvc_line)
			if m2:
			#{
				search_string = '\<pt:(\d+)\s-\s(\d+)\>'
				m3 = re.search(search_string, hvc_line)
				if debug_mode:
					print("comparing with hvc:"+hvc_line);
				if m3:
				#{
					pt1=int(m3.group(1));
					pt2=int(m3.group(2));
					if debug_mode:
						print ("hlc_pt:"+str(hlc_pt)+",pt1:"+str(pt1)+",pt2:"+str(pt2))
					#Three possible scenarios:
					#1. hlc_pt is smaller than pt1 : then move on to next hlc snapshot + increment false positive
					#2. hlc_pt is greater than or equal to pt1 and lesser than pt2 : increment true positive
					#3. hlc_pt is greater than ptt2: then move on to next hvc snapshot
					
					#check for overlap till current line i.e. current hvc-snapshot has physical time higher than the hlc-snapshot physical time
					if (pt1 > hlc_pt):
						if debug_mode:
							print("False positive ==> hlc:"+line+"hvc:"+hvc_line)
						fpv = fpv + 1; #count false positive
						break;
					elif (pt1 <= hlc_pt and hlc_pt <pt2):#overlap scenario
						if debug_mode:
							print("True positive ==> hlc:"+line+"hvc:"+hvc_line)
						tpv = tpv + 1; #count true positive
						break;
					else: #hlc_pt is greater than pt2 in the currently parsed hvc snapshot
						pass;#do nothing;# go to next line in hvc_snapshot_file
				#}
				else:
				#{
					print("No physical time in the current line. Should not happen because process id alone can never exist in a line.")
					sys.exit
				#}
			#}
			hvc_line = hvc_snapshot_file.readline() # go to next line in hvc_snapshot_file
		#}
		if debug_mode:
			print("Fetching next line in HLC snapshot file to process.")
	#}
	line = hlc_snapshot_file.readline() # go to next line in hlc_snapshot_file
#}
print("No more HLC snapshots to process. Total HLC snapshots:"+str(total_hlc_snapshots))
print("False positives:"+str(fpv))
print("True Positives:"+str(tpv))