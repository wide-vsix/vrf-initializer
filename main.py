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


def main(config):
    vrfs = config["vrfs"]
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

    if interface_all_joined:
        print("[Info]: Completed. All interfaces join to their vrf")
    else:
        print("[Warning]: All interfaces don't join to their vrf", file=sys.stderr)



if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("-d",'--daemon', help="Daemon mode. Exec eternally default: False", default=False, action='store_true')
    parser.add_argument("-t",'--timeout', help="Timeout seconds is enabled only in daemon mode. (Otherwise, it is ignored). default: 10",default=10, type=int)
    parser.add_argument("-f",'--file', help="Config file. default: ./config.json", default="./config.json", type=str)

    args = parser.parse_args()

    # Parse config
    with open(args.file, "r") as f:
        config = json.load(f)

    main(config=config)
    
    # daemon mode
    if args.daemon:
        print("[Info]: go to next cycle.")
        print(f"[Info]: sleeping {args.timeout}")
        time.sleep(args.timeout)
        main(config=config)