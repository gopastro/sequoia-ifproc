#!/usr/bin/python

from hp83711b import HP83711B
from hp83751b import HP83751B
from pmeter import PowerMeter
from ifproc_corba import IFProc
import time
import os.path

syn = HP83711B('synth')
syn_LO = HP83751B('83711b')
pmeter0 = PowerMeter('pmeter1')
pmeter1 = PowerMeter('pmeter2')
pmeter2 = PowerMeter('pmeter3')
pmeter3 = PowerMeter('pmeter4')


ifproc = IFProc()

ifmod_num = 3
chans = [8,9,10,11]

pmeters = [pmeter0,pmeter1,pmeter2,pmeter3]
Opows = [0,0,0,0]
det_vols = [0,0,0,0]
P_LSBs = [0,0,0,0]
P_USBs = [0,0,0,0]
rats = [0,0,0,0]


filename = "IFMod%d_rev2_test.txt" %(ifmod_num) #module number
dumpfile = os.path.join('/home/aleks/engineering/sequoia_tests/IFmodtests',
			  filename)
fo = open(dumpfile, "w")
fo.write('LO_freq,IF_freq,RF_freq,Atten%d,Atten%d,Atten%d,Atten%d,P_in_raw,P_in_adj,P_out%d,Dt_V%d,P_out%d,Dt_V%d,P_out%d,Dt_V%d,P_out%d,Dt_V%d\n' 
	%(chans[0],chans[1],chans[2],chans[3],chans[0],chans[0],chans[1],chans[1],
		chans[2],chans[2],chans[3],chans[3]))

filename2 = "IFMod%d_rev2_sidebandratio.txt" %(ifmod_num) #module number
dumpfile2 = os.path.join('/home/aleks/engineering/sequoia_tests/IFmodtests',
			  filename2)
fo2 = open(dumpfile2, "w")
fo2.write('LO_freq,IF_freq,Atten%d,Atten%d,Atten%d,Atten%d,P_in_raw,P_in_adj,P_LSB%d,P_USB%d,rat%d,P_LSB%d,P_USB%d,rat%d,P_LSB%d,P_USB%d,rat%d,P_LSB%d,P_USB%d,rat%d\n'
	%(chans[0],chans[1],chans[2],chans[3],chans[0],chans[0],chans[0], chans[1],chans[1],
		chans[1],chans[2],chans[2],chans[2],chans[3],chans[3],chans[3]))

syn_LO.set_power_level(5)
atten = [0,0,0,0]

for LO in range (6,21,1): #GHz


	syn_LO.set_freq(LO*1e9)
	syn.set_freq(LO*1e9 - 500*1e6)

	for i in range(0,4,1):

		channel = chans[i]
		ifproc.set_atten(atten[i],channel)
		time.sleep(.6)
		syn.set_power_level(3)
		time.sleep(.6)
		det_V = ifproc.get_voltage(channel)
		
		while abs(det_V)> 2.0:
			if det_V > 2.0:
	   			atten[i] = atten[i]+1
			elif det_V < -2.0:
	   			atten[i] = atten[i]-1
			ifproc.set_atten(atten[i],channel)
			time.sleep(.6)
			det_V = ifproc.get_voltage(channel)

		syn.set_power_level(-7)
		time.sleep(.6)
		det_low = ifproc.get_voltage(channel)
		n_itr = 0

		while(det_low < -9.0 and n_itr<2):
			atten[i] = atten[i] -1
			ifproc.set_atten(atten[chan],channel)
			time.sleep(.6)
			det_low = ifproc.get_voltage(channel)
			n_itr+=1
	

	for IF in range (100,900,100): #MHz
	
		RF_freq = (syn_LO.get_freq() - IF*1e6)
		RF = RF_freq/(1e9)
		syn.set_freq(RF_freq)
		time.sleep(.5)

		for IPow in range (-7,12,1): #dBm

			syn.set_power_level(IPow)
			time.sleep(2)
			IPow_c = IPow - 10 

			for i in range(4):

				Opows[i] = pmeters[i].get_db_power() 
				det_vols[i] = ifproc.get_voltage(chans[i])

			fo.write('%1.1f,%i,%1.1f,%i,%i,%i,%i,%1.1f,%1.1f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f\n' 
			   	%(LO,IF,RF,atten[0],atten[1],atten[2],atten[3],IPow,IPow_c,Opows[0],det_vols[0],Opows[1],det_vols[1],Opows[2],det_vols[2],Opows[3],det_vols[3]))

			if((IF==100 or IF==400 or IF==800) and LO!=20):
				if(IF==100):
					IF2 = 50
					RF2 = syn_LO.get_freq()-IF2*1e6		
					syn.set_freq(RF2)
					time.sleep(2)
				
					P_LSBs[0] = pmeters[0].get_db_power()
					P_LSBs[1] = pmeters[1].get_db_power()
					P_LSBs[2] = pmeters[2].get_db_power()
					P_LSBs[3] = pmeters[3].get_db_power()
				else:
					IF2 = IF
					P_LSBs[0] = Opows[0]
					P_LSBs[1] = Opows[1]
					P_LSBs[2] = Opows[2]
					P_LSBs[3] = Opows[3]


				syn.set_freq(syn_LO.get_freq()+IF2*1e6)
				time.sleep(4)
		
				P_LSBs[0] = pmeters[0].get_db_power()
				P_LSBs[1] = pmeters[1].get_db_power()
				P_LSBs[2] = pmeters[2].get_db_power()
				P_LSBs[3] = pmeters[3].get_db_power()

				rats[0] = (P_LSBs[0]-P_USBs[0])
				rats[1] = (P_LSBs[1]-P_USBs[1])
				rats[2] = (P_LSBs[2]-P_USBs[2])
				rats[3] = (P_LSBs[3]-P_USBs[3])

				fo2.write('%1.1f,%i,%i,%i,%i,%i,%1.1f,%1.1f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f,%1.3f\n' 
			   		%(LO,IF2,atten[0],atten[1],atten[2],atten[3],IPow,IPow_c,P_LSBs[0],P_USBs[0],rats[0],P_LSBs[1],P_USBs[1],rats[1],P_LSBs[2],P_USBs[2],rats[2],P_LSBs[3],P_USBs[3],rats[3]))
				
				syn.set_freq(RF_freq)
				time.sleep(1)
										


fo.close()
fo2.close()
		
	

