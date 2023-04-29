import os
import socket

os.system("sudo apt update")
os.system("sudo apt upgrade -y")

# Configure InfluxDB
os.system("sudo apt install influxdb-client")
os.system("influx -execute 'CREATE DATABASE SBMS'")

os.system("pip install influxdb")
os.system("sudo apt-get install python3-serial")

# Download SBMS Serial Data collector script
os.system("sudo wget --no-check-certificate --content-disposition 'https://raw.githubusercontent.com/Burtond/Electrodacus/master/sbms0-SerialToInfluxDB.py' -P '/home/SBMS0/'")
os.system("sudo wget --no-check-certificate --content-disposition 'https://raw.githubusercontent.com/Burtond/Electrodacus/master/SBMS-Logger.service' -P '/etc/systemd/system/'")

# Create a service to run collector script
os.system("sudo systemctl enable SBMS-Logger.service")
os.system("sudo systemctl start SBMS-Logger.service")

# Getting data to output to screen upon completion
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

ipaddress = get_ip_address()
os.system("curl --user admin:admin \"http://" + ipaddress + ":3000/api/datasources\" -X POST -H 'Content-Type: application/json;charset=UTF-8' --data-binary '{\"name\":\"SBMS_Data\",\"isDefault\":true ,\"type\":\"influxdb\",\"url\":\"http://influxdb:8086\",\"database\":\"SBMS\",\"access\":\"proxy\",\"basicAuth\":false}'")

print("Login to http://" + ipaddress + ":3000")
print("Username = admin, password = admin")
