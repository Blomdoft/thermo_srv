# thermo_srv
Simple storage server in python that reads BLE data from patched ATC-thermometers.

This could eventually end in a little web server that is running on a raspberry or other server.
It gathers the advertisement data from surrounding ATC Xiaomi Thermometers, which have been patched to custom firmware to actually distribute the values.

BLE is done via bleak
Storage is a SQLite database

Code is not cleaned up, and without a Webserver it is nearly useless. But I have to care for other projects at the moment so will get back to this later.
Maybe it is a starting point for someone doing something serious.

No license, do whatever you want.

