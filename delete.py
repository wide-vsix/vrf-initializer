#!/usr/bin/env python3
import subprocess
import sys
import time
import argparse
import json


def check_if(if_name):
    if_exists = (subprocess.run(f'ip link show {if_name}',shell=True,stdout=subprocess.DEVNULL).returncode == 0)
    return if_exists


def delete_vrf(vrf_name):
    command=f"ip link delete {vrf_name}"
    is_deleted = False
    try:
        subprocess.run(command,shell=True,stdout=subprocess.DEVNULL,check=True)
        is_deleted=True
    except:
        print(f"[Error]: Can not delete vrf {vrf_name}", file=sys.stderr)

    return is_deleted




if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-e",'--eternally', help="Exec eternally. default: False", default=False, action='store_true')
    parser.add_argument("-t",'--timeout', help="Timeout if failed dualing execing eternally. default: 10",default=10, type=int)
    parser.add_argument("-f",'--file', help="Config file. default: ./config.json", default="./config.json", type=str)

    args = parser.parse_args()

    # Parse config
    with open(args.file, "r") as f:
        config = json.load(f)
    vrfs = config["vrfs"]

    for vrf in vrfs:
        # check if a vrf exists
        vrf_exists = check_if(vrf['name'])
        if vrf_exists:
            delete_vrf(vrf['name'])
        