#!/usr/bin/env python3
import subprocess
import sys
import time
import argparse
import json


def create_vrf(vrf_name, vrf_id):

    is_created_vrf=False
    create_commands = [
        f"ip link add {vrf_name} type vrf table {vrf_id}",
        f"ip link set up {vrf_name}",
        f"ip addr add 127.0.0.1/8 dev {vrf_name}",
        f"ip addr add ::1/128 dev {vrf_name}"

    ]
    for command in create_commands:
        try:
            subprocess.run(command,shell=True,check=True,stdout=subprocess.DEVNULL)
        except:
            print(f"[Error]: Can not create vrf {vrf_name}", file=sys.stderr)
            break
    else:
        is_created_vrf=True
    return is_created_vrf

def check_if(if_name):
    if_exists = (subprocess.run(f'ip link show {if_name}',shell=True,stdout=subprocess.DEVNULL).returncode == 0)
    return if_exists

def join_if_to_vrf(if_name, vrf_name):
    command = f"ip link set {if_name} master {vrf_name}"
    is_joined_successfully = False

    try:
        subprocess.run(command,shell=True,check=True,stdout=subprocess.DEVNULL)
        is_joined_successfully = True
    except:
        print(f"[Error]: Can not create vrf {vrf_name}", file=sys.stderr)
    
    return is_joined_successfully 


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-e",'--eternally', help="Exec eternally. default: False", default=False, action='store_true')
    parser.add_argument("-t",'--timeout', help="Timeout if failed dualing execing eternally. default: 10",default=10, type=int)
    parser.add_argument("-f",'--file', help="Config file. default: ./config.json", default="./config.json", type=str)

    args = parser.parse_args()

    # Parse config
    with open(args.config, "r") as f:
        config = json.load(f)
    vrfs = config["vrf"]
    interfaces = config["interfaces"]


    # Check VRF exists
    for vrf in vrfs:
        if check_if(vrf['name']):
            print(f"[Info]: {vrf} is found. skip.")
        else:
            print(f"{vrf} is not found. creating...")
            is_created_successfully = create_vrf(vrf["name"],vrf["id"])
            if not is_created_successfully:
                print("[Error]: Abort ", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"[Info]: Created {vrf} ")

    # Join interface
    interface_all_joined = False

    while not interface_all_joined:
        for interface in interfaces:
            # check exists of interface and vrf.
            if_exists = check_if(interface["name"])
            vrf_exists = check_if(interface["vrf"])
            
            if not vrf_exists:
                print(f"[Error]: vrf: {interface['vrf']} does not exists.  ", file=sys.stderr)
                print("[Error]: Abort ", file=sys.stderr)
                sys.exit(1)
            if not if_exists:
                print(f"[Warning]: Interface: {interface['name']} is not found. skipping", file=sys.stderr)
                break
            # join
            is_joined_successfully = join_if_to_vrf(interface["name"], interface["vrf"])
            if is_joined_successfully:
                print(f"[Info]: Joined if:{interface['name']} to vrf:{interface['vrf']} ")
        else:
            # 一度もbreakせずに完遂
            interface_all_joined = True
            break
        # 途中でbreakされた場合
        if args.eternally:
            print(f"[Info]: Retry after {args.timeout} sec.")
            time.sleep(args.timeout)
        else:
            print("[Error]: Abort ", file=sys.stderr)
            sys.exit(1)
    
    print("[Info]: Completed ")
    sys.exit(0)
