# thermo_srv
Simple storage server in python that reads BLE data from patched ATC-thermometers.

This could eventually end in a little web server that is running on a raspberry or other server.
It gathers the advertisement data from surrounding ATC Xiaomi Thermometers, which have been patched to custom firmware to actually distribute the values.

BLE is done via bleak
Storage is a SQLite database

Code is not cleaned up, but it now has a little webserver build in. Need to configure that correctly before it is actually useful

No license, do whatever you want.

