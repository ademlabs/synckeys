#!/usr/bin/env python

import configparser
import argparse
import os#, subprocess
import shutil
import codecs
from datetime import datetime

def format_hex(hex_string):
    return hex_string.replace('hex:', '').replace(',', '').upper()


def format_hex_b(hex_string):
    hex_parts = hex_string.replace('hex(b):', '').split(',').reverse()
    hex = ''.join(hex_parts)

    return hex

def format_dword(dword_string):
    dword = dword_string.replace('dword:', '')

    return dword


def format_mac_address(mac_string):
    address = mac_string.upper()
    address_parts = [address[i:i + 2] for i in range(0, len(address), 2)]

    return ':'.join(address_parts)


def load_keys_from_file(file_path):
    # Load full file contents and clean up into a config parseable format
    with codecs.open(file_path, 'r', 'utf-16-le') as f:
        contents = f.read()
        contents = contents.replace('"', '').replace('=', ' = ').replace('HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys\\', '').split('\r\n')
        del contents[0:4]
        config_contents = '\n'.join(contents)
        print(config_contents)
        # Parse the contents into a configuration structure
        parsed_config = configparser.ConfigParser()
        parsed_config.read_string(config_contents)

        return parsed_config


def get_device_path(adapter_mac, device_mac):
    return f'/var/lib/bluetooth/{adapter_mac}/{device_mac}'


def backup_device_info_file(adapter_mac, device_mac):
    device_path = get_device_path(adapter_mac, device_mac)
    now = datetime.now()
    current_datetime = now.strftime("%Y%m%d%H%M%S")
    #process = subprocess.run(['sudo', 'cp', f'{device_path}/info', f'{device_path}/info-{current_datetime}'], stdout = subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    shutil.copyfile(f'{device_path}/info', f'{device_path}/info-{current_datetime}')


def get_system_pairing(adapter_mac, device_mac):
    device_path = get_device_path(adapter_mac, device_mac)
    info_file = f'{device_path}/info'
    #process = subprocess.run(['sudo', 'cat', f'{device_path}/info'], stdout = subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    #if process.returncode != 0 and 'No such file or directory' in process.stderr:
    #    return None

    if not os.path.isfile(info_file):
        return None

    # Read info data into a config structure
    pairing_config = configparser.ConfigParser()
    pairing_config.optionxform = str
    #pairing_config.read_string(process.stdout)
    pairing_config.read(info_file)

    return pairing_config


def update_system_pairing(adapter_mac, device_mac, config):
    backup_device_info_file(adapter_mac, device_mac)
    # Write config structure back to info file
    device_path = get_device_path(adapter_mac, device_mac)
    info_file = open(f'{device_path}/info', 'w')
    config.write(info_file)
    info_file.close()


def process_basic_pairing(adapter_config):
    adapter_mac = format_mac_address(adapter_config.name)
    print("Bluetooth Adapter:", adapter_mac)
    # Iterate through each device and pairing key from the dumped registry config
    print(" Checking devices:")
    for device, pairing_key in adapter_config.items():
        if device == 'masterirk':
            continue
        device_mac = format_mac_address(device)
        pairing_key = format_hex(pairing_key)
        print(f" {device_mac} ", end='')

        # Check this adapter's paired devices in the current Linux system
        paired_config = get_system_pairing(adapter_mac, device_mac)
        if paired_config == None:
            print('(# not paired #)')
            continue
        # Get paired device name
        device_name = paired_config['General']['Name']
        device_alias = paired_config['General']['Alias']
        print(f"({device_name} / {device_alias})")
        current_key = paired_config['LinkKey']['Key']

        # Check whether current system key already matches key from Windows
        #if current_key == pairing_key:
        #    print(f'  # Current key {current_key} already matches new key {pairing_key}')
        #    continue

        action = input(f'  > Replace current key {current_key} with new key {pairing_key}? (y/N): ')
        if action.lower() != 'y':
            continue

        # Replace system key
        paired_config['LinkKey']['Key'] = pairing_key
        update_system_pairing(adapter_mac, device_mac, paired_config)


def process_devices(config):
    # Sort the list of adapters and adapter\device pairs to make sequential parsing easier
    adapter_devices = sorted(config.sections())
    for device in adapter_devices:
        if not '\\' in device:
            process_basic_pairing(config[device])
        else:
            extract_pairing_params(config[device])
        exit()


def parse_args():
    parser = argparse.ArgumentParser(description="SyncKeys - Update Linux Bluetooth keys from Windows-paired devices")
    parser.add_argument('keyfile', help='Path to exported Windows Registry (.reg) file.')

    return parser.parse_args()


def main():
    args = parse_args()
    #setattr(args, 'keyfile', 'mykeys.reg')
    print(args)
    config = load_keys_from_file(args.keyfile)
    process_devices(config)


if __name__ == '__main__':
    main()