#!/usr/bin/python3

import argparse
import re
import subprocess
import ipaddress

IP_HEADER_SIZE = 20
ICMP_HEADER_SIZE = 8

def check_host_validity(host):
    reg_exp = re.compile(
        r'^(?:'
        r'(?:(?!-)[A-Z\d-]{1,63}(?<!-)\.)+(?:[A-Z]{2,13})'  # Hostname
        r'|'
        r'\d{1,3}(?:\.\d{1,3}){3}'  # IPv4
        r')$',
        re.IGNORECASE
    )
    return reg_exp.match(host)


def check_icmp():
    process = subprocess.run(
        ["cat", "/proc/sys/net/ipv4/icmp_echo_ignore_all"],
        capture_output = True,
        text = True
    )

    if process.returncode != 0:
        print("Subprocess 'cat /proc/sys/net/ipv4/icmp_echo_ignore_all' exited with code", process.returncode)
        print(process.stderr)
        exit(1)

    if process.stdout == "1":
        return False
    
    return True


def ping_host(host, packet_size):
    process = subprocess.run(
        ['ping', '-c', '1', '-M', 'do', '-s', str(packet_size), host],
        capture_output = True,
        text = True
    )
    return process

    
def calc_mtu(host):
    l, r = 0, 9001 - IP_HEADER_SIZE - ICMP_HEADER_SIZE
    while r - l > 1:
        mid = (l + r) // 2
        process = ping_host(host, mid)
        if process.returncode == 0:
            l = mid
        elif process.returncode == 1:
            r = mid
        else:
            print(process.stderr)
            exit(1)
    return l


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    
    args = parser.parse_args()
    host = args.host
    host_valid = check_host_validity(host)
    if not host_valid:
        print("Host", host, "is not valid")
        exit(1)

    if not check_icmp():
        print("ICMP is disabled")
        exit(1)

    mtu = calc_mtu(host)
    print("Minimal MTU is", mtu + IP_HEADER_SIZE + ICMP_HEADER_SIZE)

if __name__ == '__main__':
    main()
