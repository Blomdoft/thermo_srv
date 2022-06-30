# This is a sample Python script.

import asyncio
import loggingconfig
import logging
from bleak import BleakScanner
from Measures import Measures
from MeasuresSQLitePersister import MeasuresSQLitePersister

LOG = logging.getLogger("Main")


def detection_callback(device, advertisement_data):

    LOG.debug("Advertisement received " + str(advertisement_data))

    if advertisement_data.local_name is not None and advertisement_data.local_name.startswith("ATC"):
        data_str = list(advertisement_data.service_data.values())[0]
        name = advertisement_data.local_name
        temp = int.from_bytes(data_str[6:8], "big", signed=True) / 10
        hum = data_str[8]
        Measures().add_measure(name, temp, hum)


async def main():
    loggingconfig.load_logging_config()

    LOG.info("Initializing Measures and Scanner")

    Measures().set_store(MeasuresSQLitePersister("../../measures.db"))
    Measures().load()
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)

    try:
        while True:
            LOG.info("Starting Scan")
            await scanner.start()
            await asyncio.sleep(30.0)
            LOG.info("...Stopping Scan")
            await scanner.stop()
            Measures().save()
            Measures().house_keep()
    except KeyboardInterrupt:
        Measures().save()
        await scanner.stop()

asyncio.run(main())
