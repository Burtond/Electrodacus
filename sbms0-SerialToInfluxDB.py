
#!/usr/bin/env python


"""
  2020-05-26

  Created 22 April 2007
  By David A. Mellis  <dam@mellis.org>
  modified 2020-05-26
  by David Buron
   
  This example code is in the public domain.
  
"""

import sys
import time
import serial
from influxdb import InfluxDBClient

#Environment specific parameters based on how you setup your database
#Name of the InfluxDB
dbname = "SBMS"
#InfluxDB Measurement/Index
dbmeasurement = "SBMS_Metrics"
#InfluxDB instance, I use this as a tag to filter for multiple SBMS0 data feeds
dbinstance = "SBMS0a"

#BAUD rate configured on SBMS0 serial connection
sbmsbaud = 115200

# p - location of the data in the string, starting at 0!
# s - size of the data (for example, SOC is 2)
# d - the name of the variable in this case var sbms
def dcmp(p, s, d):

    xx = 0;

    for z in range(s):
# Java script: xx = xx + ((d.charCodeAt((p + s - 1) -z) -35) * Math.pow(91, z$))
        wanted_ascii_character = ord(d[(p + s - 1) - z])
        xx = xx + ((wanted_ascii_character - 35) * pow(91, z))

    return xx

#Connect to local InfluxDB and Database
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database(dbname)

#Open Serial connection from USB, SBMS0 must be set to same BAUD rate
ser = serial.Serial('/dev/ttyUSB0', sbmsbaud)

var_sbms = ''

# Receiving Data
while True:
	data =  ser.readline()
	if not data:
		break
	var_sbms = data

#Debug output from SBMS0
#	print(var_sbms)
#	print(str(dcmp(0, 27, var_sbms)) + str(var_sbms[28]) + str(dcmp(29, len(var_sbms)-29, var_sbms)))
	
# process the SBMS data
	SOC = float(dcmp(6, 2, var_sbms))
#    print('PV SOC = ' + str(SOC) + '%')

# one of cell voltage has to be cast to a float
	Cell1 = float(dcmp(8, 2, var_sbms)) / 1000
#   print('Cell1 = ' + str(Cell1) + '\n')

	Cell2 = float(dcmp(10, 2, var_sbms)) / 1000
#    print('Cell2 = ' + str(Cell2) + '\n')

	Cell3 = float(dcmp(12, 2, var_sbms)) / 1000
#    print('Cell3 = ' + str(Cell3) + '\n')

	Cell4 = float(dcmp(14, 2, var_sbms)) / 1000
#    print('Cell4 = ' + str(Cell4) + '\n')

	Cell5 = float(dcmp(16, 2, var_sbms)) / 10009
#    print('Cell5 = ' + str(Cell5) + '\n')

	Cell6 = float(dcmp(18, 2, var_sbms)) / 1000
#    print('Cell6 = ' + str(Cell6) + '\n')

	Cell7 = float(dcmp(20, 2, var_sbms)) / 1000
#    print('Cell7 = ' + str(Cell7) + '\n')

	Cell8 = float(dcmp(22, 2, var_sbms)) / 1000
#    print('Cell8 = ' + str(Cell8) + '\n')

# Converted based on documentation: 0 to 1449 = -45C to 99.9C
# Converting to fahrenheit
	Internal_temp = float((dcmp(24, 2, var_sbms)-450)/10*9/5+32)
	Internal_temp = round(Internal_temp,3)
#    print('Internal temp = ' + str(Internal_temp) + '\n')

# Converted based on documentation: 0 to 1449 = -45C to 99.9C
# Converting to fahrenheit
	External_temp = float((dcmp(26, 2, var_sbms)-450)/10*9/5+32)
	External_temp = round(External_temp,3)
#    print('External temp = ' + str(External_temp) + '\n') 

# Bat + and - sign at [28] is not compressed
	sign = var_sbms[28]

	Batt_current = round(float(dcmp(29, 3, var_sbms))/1000,3)
	if(sign == '-'):
		Batt_current = (-1)*Batt_current
#	print('Battery current = ' + str(Batt_current) + '\n')

	PV1 = float(dcmp(32, 3, var_sbms))
#    print('PV1 current = ' + str(PV1) + '\n')

	PV2 = float(dcmp(35, 3, var_sbms))
#    print('PV2 current = ' + str(PV2) + '\n')

	External_load = (dcmp(38, 3, var_sbms))
#	print('External load current = ' + str(External_load) + '\n')

	ADC2 = float(dcmp(41, 3, var_sbms))
#	print('ADC2 = ' + str(ADC2) + '\n')

	ADC3 = float(dcmp(44, 3, var_sbms))
#	print('ADC3 = ' + str(ADC3) + '\n')

	ADC4 = float(dcmp(47, 3, var_sbms))
#	print('ADC4 = ' + str(ADC4) + '\n')

	heat1 = float(dcmp(50, 3, var_sbms))
#    print('heat1 = ' + str(heat1) + '\n')

	heat2 = float(dcmp(53, 3, var_sbms))
#     print('heat2 = ' + str(heat2) + '\n')

	ERR = dcmp(56, 3, var_sbms)
#    print('ERR_code = '+ str(ERR) + 'change to binary\n')

# calculations
	Battery_voltage = (Cell1 +  Cell2 + Cell3 + Cell4 + Cell5 + Cell6 + Cell7 + Cell8)
	Battery_voltage = round(Battery_voltage, 3)
#    print('Battery voltage = ' + str(Battery_voltage) + 'V')

# External load
	External_load = float(External_load / 1000)
	External_load = round(External_load, 3)
#    print('External Load current =  ' + str(External_load) + 'A')

# Total PV current
	PV_total_current = (PV1 + PV2) / 1000
	PV_total_current = round(PV_total_current, 3)

#    print('Total PV current = ' + str(PV_total_current) + 'A')

#Converting error to binary
	Error_Binary = '{0:08b}'.format(ERR)

#Capturing SBMS0 flag values to array    
	flags = []
	if(ERR & 16384):
		flags.append('DFET')
	if(ERR & 8192):
		flags.append('EOC')
	if(ERR & 4096):
		flags.append('CFET')
	if(ERR & 2048):
		flags.append('ECCF')
	if(ERR & 1024):
		flags.append('LVC')
	if(ERR & 512):
		flags.append('OPEN')
	if(ERR & 256):
		flags.append('CELF')
	if(ERR & 128):
		flags.append('DSC')
	if(ERR & 64):
		flags.append('DOC')
	if(ERR & 32):
		flags.append('COC')
	if(ERR & 16):
		flags.append('IOT')
	if(ERR & 8):
		flags.append('UVLK')
	if(ERR & 4):
		flags.append('UV')
	if(ERR & 2):
		flags.append('OVLK')
	if(ERR & 1):
		flags.append('OV')

# Joining flags to a single string for simple output
	separator = ", "
	flags = separator.join(flags)

# Create DB payload
	json_body = [
	{
		"measurement": dbmeasurement,
		"tags": {
			"Name": dbinstance
		},
		"fields": {
			"External Temperature": External_temp,
			"Internal Temperature": Internal_temp,
			"Monitor Flags": flags,
			"Battery Voltage": Battery_voltage,
			"Battery Current": Batt_current,
			"PV Total Current": PV_total_current,
			"PV1": PV1,
			"PV2": PV2,
			"External Load": External_load,
			"State of Charge": SOC,
			"ADC2": ADC2,
			"ADC3": ADC3,
			"ADC4": ADC4,
			"Heat 1": heat1,
			"Heat 2": heat2,
			"Cell 1": Cell1,
			"Cell 2": Cell2,
			"Cell 3": Cell3,
			"Cell 4": Cell4,
			"Cell 5": Cell5,
			"Cell 6": Cell6,
			"Cell 7": Cell7,
			"Cell 8": Cell8
			}
		}
	]
# Write to DB
	client.write_points(json_body)
