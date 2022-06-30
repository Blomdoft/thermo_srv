import logging
from datetime import datetime

LOG = logging.getLogger("Measures")


class MeasureStoreInterface(object):
    """load existing data"""
    def load_data(self) -> dict:
        pass

    """save new or updated data"""
    def save_data(self, measures):
        pass


class Measure(object):

    def __init__(self, name, timestamp, temperature, humidity):
        self.name = name
        self.timestamp = timestamp
        self.temperature = temperature
        self.humidity = humidity

    def __str__(self):
        return "Measure (name: " + self.name + ", timestamp: " + str(self.timestamp) + ", temp: "\
               + str(self.temperature) + ", hum: " + str(self.humidity) + ") "


class Measures(object):
    measures = {}
    store = None

    """ Singleton """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Measures, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def set_store(self, measure_store: MeasureStoreInterface):
        self.store = measure_store

    def load(self):
        if self.store is not None:
            ms = self.store.load_data()
            if ms is not None:
                self.measures = ms

    def save(self):
        if self.store is not None:
            self.store.save_data(self.measures)

    def add_measure(self, name, temperature, humidity):
        timestamp = datetime.now()
        new_measure = Measure(name, timestamp, temperature, humidity)

        if name not in self.measures:
            self.measures[name] = []

        """ only store if last entry is more than a minute old """
        if len(self.measures[name]) == 0 or (timestamp-self.measures[name][-1].timestamp).total_seconds() > 60:
            self.measures[name].append(new_measure)
            LOG.info("Appending measure " + str(new_measure))
        else:
            LOG.info("Discarding measure " + str(new_measure))

    def get_current_measures(self):
        return_list = []

        for key in self.measures:
            return_list.append(self.measures[key][-1])
        return return_list

    def house_keep(self):
        """ Reduce the existing lists so that no more than two days at max is stored,
            day at max has 24*60*2 = 2880 records ... okay this is a terrible way to do it *g*, but I go for it"""
        for key in self.measures:
            size = len(self.measures[key])
            if size > 2880:
                remove_chunk = size-2880
                LOG.info("Housekeeping, removing first " + str(remove_chunk) + " elements from device " + key)
                del (self.measures[key][0:remove_chunk])
            else:
                LOG.info("Housekeeping, not removing elements from device " + key + ", only accumulated "
                         + str(size) + " entries.")
