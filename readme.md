# BlueSync - Sync dual-boot Bluetooth devices
Syncronize your Bluetooth device pairing keys from Windows to Linux.

## Warning / Disclaimer
> The code and instructions within this project accesses and modifies system files on your Windows and Linux installations. Although care has been taken to ensure that nothing harmful happens, there could be a risk of damage to your software and hardware. Your usage of the program and instructions herein constitutes acceptance of those risks and the author cannot be held liable for any claims whatsoever.

## Pre-requisites
On Linux you need the following:
1. Python 3 installed on your Linux system.
2. This project downloaded on your Linux system, or at least the `synckeys.py` file.
3. **sudo** / **root** access.

On Windows you need the following:
1. [PSExec](http://live.sysinternals.com/psexec.exe) downloaded and accessible via the command line. E.g. downloaded to the root of your C:\ drive.
2. **Administrator** access.

## Instructions
1. Boot into your Linux installation and pair all the devices that you wish to share with your Windows system. This is necessary to create the required initial pairing configurations.
2. Reboot into your Windows system and pair the same devices again. We will use the keys generated from this OS.
3. Open a command prompt in **Administrator** mode and navigate to the directory where you downloaded [PSExec](http://live.sysinternals.com/psexec.exe) into. Run the following command to dump the keys:
```
psexec -s -i regedit /e c:\keydump.reg HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Services\BTHPORT\Parameters\Keys
```
4. Copy the file from `c:\keydump.reg` into a removeable storage or a location which is accessible by your Linux system.
5. Reboot into your Linux system.
6. Copy the `keydump.reg` file to an accessible location in your Linux filesystem.
7. Open a terminal and navigate to the location where `synckeys.py` is located.
8. Run the `synckeys.py` Python 3 script with **root** or **sudo**:
```
sudo ./synckeys.py /path/to/keydump.reg
```
9. The adapters and devices from the key dump will be compared to the pairing in Linux and if a difference is detected, it will prompt you to update the keys. You can choose Yes or No (default). If you choose `Yes`, a timestamped backup file is created in the `/var/lib/bluetooth/{ADAPTER_MAC}/{DEVICE_MAC}` directory before the update is performed.
```
Bluetooth Adapter - 7C:B2:7D:57:EA:D5
  DC:0C:2D:ED:01:65 (# not paired #)
  04:00:00:00:6A:8B (# not paired #)

  0C:E0:E4:C8:27:5D (PLT_BBTSENSE / PLT_BBTSENSE)
    | LinkKey: 63C1F72FB8E5F474AED058019A834FDA > No change required.

  F3:46:AD:D7:53:3C (Orochi V2 / Orochi V2)
    | IdentityResolvingKey: BB123FA60524A22A5AF33EE83514FF0B > Update to: AA764EA60524A76A5AF50EE49463ED0C
    | LongTermKey: 28513DB654511A7346BDA3F676CAE7F8 > Update to: 85140DC915611A7346ECD3F676CFF7E9
    |   EncSize: 16 > No change required.
    |   EDiv: 43465 > Update to: 74325
    |   Rand: 5734307009814747306 > Update to: 9876302985738291827
    > Update keys for device? (y/N): y
    > OK!
```
10. Once the keys are updated, you can restart the bluetooth service with the following (or the equivalent on your system):
```
sudo systemctl restart bluetooth
```

## Issues
I haven't found any issues up to now but I also have a limited number of devices on which I can test. Feel free to create a GitHub issue describing your problem and I'll try to take a look. If you know how to fix the code, feel free to submit a PR and I'll include it after reviewing.