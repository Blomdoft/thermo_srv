import os.path
import sqlite3
import logging
from datetime import datetime
from sqlite3 import Error
from Measures import MeasureStoreInterface, Measure

LOG = logging.getLogger("MeasuresSQLPersister")

sql_create_measures_table = """ CREATE TABLE IF NOT EXISTS measures (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    timestamp DATETIME NOT NULL,
                                    temp INTEGER NOT NULL,
                                    hum INTEGER NOT NULL
                                ); """

sql_get_latest_timestamp = """ SELECT max(timestamp) FROM measures; """


sql_get_historic_entries = """ SELECT timestamp, temp, hum FROM measures WHERE name = ? ORDER BY timestamp DESC LIMIT 2880; """

sql_get_device_names = """ SELECT DISTINCT name FROM measures; """

sql_insert_measure = """ INSERT INTO measures (name, timestamp, temp, hum) 
                            VALUES (?, ?, ?, ?); """


class MeasuresSQLitePersister(MeasureStoreInterface):
    conn = None

    def initialize_db(self):
        c = self.conn.cursor()
        c.execute(sql_create_measures_table)

    def __init__(self, filename):
        LOG.info("Starting database persister")
        try:

            if not os.path.exists(filename):
                LOG.info("Creating new database " + filename)
                self.conn = sqlite3.connect(filename)
                self.initialize_db()
            self.conn = sqlite3.connect(filename)
            LOG.info("Using database" + filename)
        except Error as e:
            LOG.error("Unable to utilize database under " + filename + " : " + e.sqlite_errorname)
            quit(1)

    """load existing data"""
    def load_data(self) -> dict:
        c = self.conn.cursor()
        c.execute(sql_get_device_names)
        rows = c.fetchall()
        LOG.info("Reading for " + str(len(rows)) + " devices from database.")
        return_measures = {}
        for row in rows:
            name = row[0]
            c.execute(sql_get_historic_entries, (name,))
            db_measures = c.fetchall()
            LOG.info("Reading " + str(len(db_measures)) + " measures back for device " + name)
            measures = []
            for db_measure in db_measures:
                measures.append(Measure(
                                        name,
                                        datetime.strptime(db_measure[0], '%Y-%m-%d %H:%M:%S.%f'),
                                        float(db_measure[1]/10),
                                        db_measure[2]))
            measures.reverse()
            return_measures[name] = measures
        return return_measures

    """save new or updated data"""
    def save_data(self, measures: dict):

        LOG.info("Saving new measures")

        """ get latest timestamp from current database """
        c = self.conn.cursor()
        c.execute(sql_get_latest_timestamp)
        latest_timestamp = datetime.min
        if c.arraysize > 0:
            dbdate = c.fetchone()[0]
            if dbdate is not None:
                latest_timestamp = datetime.strptime(dbdate,
                                                     '%Y-%m-%d %H:%M:%S.%f')
        LOG.info("Last timestamp on database " + latest_timestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)"))

        measures_to_save = []
        """ filter all measures that are already stored on database """
        for measure_list in measures.values():
            for measure in measure_list:
                if measure.timestamp > latest_timestamp:
                    measures_to_save.append(measure)

        LOG.info("Number of new measures to save " + str(len(measures_to_save)))

        """ store new measures """
        for measure in measures_to_save:
            c.execute(sql_insert_measure, (measure.name, measure.timestamp, measure.temperature * 10, measure.humidity))
        self.conn.commit()
