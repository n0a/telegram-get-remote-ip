#!/usr/bin/env bash

# This is tool for get telegram caller IP address by using XOR-MAPPED-ADDRESS.
# Tested on macOS Catalina and Kali Linux. Probably will work with root android phone.
# by n0a 2020
# https://n0a.pw

CAP_PATH="/tmp/tg_cap$RANDOM.pcap"	#Temporary catch path pcap
CAP_TEXT="/tmp/tg_text$RANDOM.txt"	#Temporary text info
CAP_DURATION="5"					#Capture duration in seconds
MY_IP=$(curl -s icanhazip.com)		#Get external ip. ident.me, ifconfig.me also works.

if ! command -v tshark &> /dev/null
then
	echo "[-] tshark could not be found. Try to install tshark first."
	echo "[+] Debian based: sudo apt-get install -y tshark"
	echo "[+] RedHat based: sudo yum install -y tshark"
	exit 1
fi
echo "[+] Telegram get caller IP v0.1"
echo "[+] Start tshark for catch traffic. Wait for $CAP_DURATION seconds..."

tshark -w $CAP_PATH -a duration:$CAP_DURATION > /dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "[+] Traffic is captured."	
else
	echo "[-] Error with traffic capture. Try run script with sudo."
	exit 1	
fi

tshark -r $CAP_PATH > $CAP_TEXT 2>/dev/null
if [ $? -eq 0 ]; then
	echo "[+] Converting pcap succesfully."
else
	echo "[-] Error converting pcap from $CAP_PATH to $CAP_TEXT."
	exit 1
fi
if grep -q "STUN 106" $CAP_TEXT
then 
	echo "[+] Telegram traffic was found.";
else
	echo "[-] Telegram traffic could not be found.";
	echo "[!] "
	echo "[!] Run this script only >>>AFTER<<< answer";
	echo "[!] "
	exit 1
fi

TG_OUT=$(cat $CAP_TEXT | grep "STUN 106" | sed 's/^.*XOR-MAPPED-ADDRESS: //' | awk '{match($0,/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/); ip = substr($0,RSTART,RLENGTH); print ip}' | awk '!seen[$0]++')
IP_1=$(echo $TG_OUT | awk '{print $1}')
IP_2=$(echo $TG_OUT | awk '{print $2}')
#echo $IP_1
#echo $IP_2
#echo $MY_IP
if [ $MY_IP == $IP_1 ]; then
	IP=$IP_2
elif [ $MY_IP == $IP_2 ]; then
	IP=$IP_1
else
	IP="[-] Sorry. IP not found."
	exit 1
fi
HOST=$(host $IP)
echo "[+] "
echo "[+] IP:   $IP"
echo "[+] HOST: $HOST"
echo "[+] "
rm $CAP_PATH && rm $CAP_TEXT
if [ $? -eq 0 ]; then
	echo "[+] Cleanup temporary files."
else
	echo "[-] Error cleanup. Check $CAP_PATH and $CAP_TEXT."
	exit 1
fi

while true; do
	read -p "[?] Run whois $IP? (Y/N): " -n 1 -r yn
	case $yn in
		[Yy]* ) whois $IP; break;;
		[Nn]* ) echo -e "\n[+] Bye bye!"; exit;;
		* ) echo "Please answer Y or N.";;
	esac
done
