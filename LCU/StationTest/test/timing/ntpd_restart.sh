#!/bin/sh
# 1.1 restart ntpd time demon
# 24-11-2016, M.J. Norden

echo "restart ntpd time server"
#sudo /etc/init.d/ntpd restart
sudo service ntpd restart

