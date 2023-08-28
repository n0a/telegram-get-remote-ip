# This script is intended to be used to determine the IP address of the interlocutor in the telegram messenger.
# You must have tshark installed to use it.
# Tested on macOS 13.4.1 and Ubuntu Linux 20.
# Probably will be working on android phone with root permissions and termux.
# by n0a 2020-2023
# https://n0a.pw

import ipaddress
import netifaces
import requests
import argparse
import platform
import pyshark
import socket
import sys
import os


def check_tshark_availability():
    """Check Tshark install."""
    tshark_path = os.popen('which tshark').read().strip()

    if not tshark_path:
        os_type = platform.system()
        if os_type == "Linux":
            print("Install tshark first: sudo apt update && apt install tshark")
        elif os_type == "Darwin":  # macOS
            print("Install Wireshark first: https://www.wireshark.org/download.html")
        else:
            print("Please install tshark.")
        sys.exit(1)
    else:
        print("[+] tshark is available.")


# Telegram AS list of excluded IP ranges
EXCLUDED_NETWORKS = ['91.108.13.0/24', '149.154.160.0/21', '149.154.160.0/22',
                     '149.154.160.0/23', '149.154.162.0/23', '149.154.164.0/22',
                     '149.154.164.0/23', '149.154.166.0/23', '149.154.168.0/22',
                     '149.154.172.0/22', '185.76.151.0/24', '91.105.192.0/23',
                     '91.108.12.0/22', '91.108.16.0/22', '91.108.20.0/22',
                     '91.108.4.0/22', '91.108.56.0/22', '91.108.56.0/23',
                     '91.108.58.0/23', '91.108.8.0/22', '95.161.64.0/20']


def get_hostname(ip):
    """Retrieve hostname for the given IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None


def get_my_ip():
    """Retrieve the external IP address."""
    try:
        return requests.get('https://icanhazip.com').text.strip()
    except Exception as e:
        print(f"[!] Error fetching external IP: {e}")
        return None


def get_whois_info(ip):
    """Retrieve whois data for the given IP."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()

        # Get the hostname using the socket library
        hostname = get_hostname(ip)
        if hostname:
            print(f"[+] Hostname: {hostname}")

        return data
    except Exception as e:
        print(f"[!] Error fetching whois data: {e}")
        return None


def display_whois_info(data):
    """Display the fetched whois data."""
    if not data:
        return

    print(f"[!] Country: {data.get('country', 'N/A')}")
    print(f"[!] Country Code: {data.get('countryCode', 'N/A')}")
    print(f"[!] Region: {data.get('region', 'N/A')}")
    print(f"[!] Region Name: {data.get('regionName', 'N/A')}")
    print(f"[!] City: {data.get('city', 'N/A')}")
    print(f"[!] Zip Code: {data.get('zip', 'N/A')}")
    print(f"[!] Latitude: {data.get('lat', 'N/A')}")
    print(f"[!] Longitude: {data.get('lon', 'N/A')}")
    print(f"[!] Time Zone: {data.get('timezone', 'N/A')}")
    print(f"[!] ISP: {data.get('isp', 'N/A')}")
    print(f"[!] Organization: {data.get('org', 'N/A')}")
    print(f"[!] AS: {data.get('as', 'N/A')}")


def is_excluded_ip(ip):
    """Check if IP is in the excluded list."""
    for network in EXCLUDED_NETWORKS:
        if ipaddress.ip_address(ip) in ipaddress.ip_network(network):
            return True
    return False


def choose_interface():
    """Prompt the user to select a network interface."""
    interfaces = netifaces.interfaces()
    print("[+] Available interfaces:")
    for idx, iface in enumerate(interfaces, 1):
        print(f"{idx}. {iface}")
    choice = int(input("[+] Enter the number of the interface you want to use: "))
    return interfaces[choice - 1]


def extract_stun_xor_mapped_address(interface):
    """Capture packets and extract the IP address from STUN protocol."""
    print("[+] Capturing traffic, please wait...")

    cap = pyshark.LiveCapture(interface=interface, display_filter="stun")
    my_ip = get_my_ip()

    for packet in cap.sniff_continuously(packet_count=250):
        if hasattr(packet, 'ip'):
            src_ip = packet.ip.src
            dst_ip = packet.ip.dst

            if is_excluded_ip(src_ip) or is_excluded_ip(dst_ip):
                continue

            if packet.stun:
                xor_mapped_address = packet.stun.get_field_value('stun.att.ipv4')

                if xor_mapped_address:
                    if xor_mapped_address != my_ip:
                        return xor_mapped_address
    return None


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Determine the IP address of the interlocutor in the Telegram messenger.')
    parser.add_argument('-i', '--interface', help='Network interface to use', default=None)
    return parser.parse_args()


def main():
    try:
        check_tshark_availability()
        args = parse_arguments()

        if args.interface:
            interface_name = args.interface
        else:
            interface_name = choose_interface()

        address = extract_stun_xor_mapped_address(interface_name)
        if address:
            print(f"[+] SUCCESS! IP Address: {address}")
            whois_data = get_whois_info(address)
            display_whois_info(whois_data)
        else:
            print("[!] Couldn't determine the IP address of the peer.")
    except (KeyboardInterrupt, EOFError):
        print("\n[+] Exiting gracefully...")
        pass


if __name__ == "__main__":
    main()
