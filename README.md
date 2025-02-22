# Main
This repository contains a network slicing solution, programmed using P4. The corresponding code can be run by Intel Tofino Chips.
The main goal of this NSS was to achieve network slicing, which was implemented using a Two Rate Three Color Marker as defined in RFC 2698.
Following the traditional SDN principle, this repository contains the data plane. Refer to [p4slice_api](https://github.com/Selfie21/p4slice_api) for the corresponding control plane.

# Setup
In order to run this module you need an installation of P4Studio at your deposition. Simply call `compile.sh slice`, which will compile the program and run the necessary P4Studio commands. 

# Testing
If you want to perform some local testing, refer to the network folder. It contains a `network.py` file which can be used to configure various mininet instances.
Do not worry I did not leak IP adresses, they were all made up to be used inside of a test network.
