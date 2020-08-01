import os
import socket

os.system("apt update")
os.system("apt upgrade -y")

# Install & configure InfluxDB
os.system("wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -")
os.system("'deb https://repos.influxdata.com/debian buster stable' | sudo tee /etc/apt/sources.list.d/influxdb.list")
os.system("apt update")
os.system("apt install influxdb")
os.system("systemctl unmask influxdb")
os.system("systemctl enable influxdb")
os.system("systemctl start influxdb")
os.system("sudo apt install influxdb-client")
os.system("influx -execute 'CREATE DATABASE SBMS'")

os.system("apt-get -y install python-influxdb")
os.system("sudo apt-get install python-serial")

# Install Grafana
os.system("apt-get install -y adduser libfontconfig1")
# Package for Intel based install
#os.system("wget https://dl.grafana.com/oss/release/grafana_7.1.1_amd64.deb")
#os.system("sudo dpkg -i grafana_7.1.1_amd64.deb")

os.system("wget https://dl.grafana.com/oss/release/grafana_7.1.1_armhf.deb")
os.system("dpkg -i grafana_7.1.1_armhf.deb")
os.system("systemctl enable grafana-server")
os.system("systemctl start grafana-server")

os.system("sudo wget --no-check-certificate --content-disposition 'https://raw.githubusercontent.com/Burtond/Electrodacus/master/sbms0-SerialToInfluxDB.py' -P '/home/SBMS0/'")

f = open("/etc/systemd/system/SBMS-Logger.service","w")
f.write('[Unit]\n')
f.write('Description=Serial logging service for SBMS0 charge controller python script\n')
f.write('After=influxdb.service\n')
f.write('[Service]\n')
f.write('ExecStart=sudo python /home/SBMS0/sbms0-SerialToInfluxDB.py\n')
f.write('Restart=always\n')
f.write('StandardOutput=syslog\n')
f.write('StandardError=syslog\n')
f.write('SyslogIdentifier=SBMS\n')
f.write('User=pi\n')
f.write('Group=pi\n')
f.write('[Install]\n')
f.write('WantedBy=multi-user.target\n')
f.close()

os.system("systemctl enable SBMS-Logger.service")
os.system("systemctl start SBMS-Logger.service")

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

ipaddress = get_ip_address()
print "Login to https://" + ipaddress + ":3000"
print "Username = admin, password = admin"
