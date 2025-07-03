from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import logging
from Measures import Measures

LOG = logging.getLogger("MeasureServer")


class MeasuresServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "service" in self.path:
            self.handle_rest_service_call()
        else:
            self.handle_html_call()

    def handle_html_call(self):
        props = load_properties("./deviceNames.properties")
        current = Measures().get_current_measures()

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        with open('./Measures_Template.html') as f:
            template = " ".join([l.rstrip("\n") for l in f])
            block_start = template.find("<!-- block -->")
            block_end = template.find("<!-- end_block -->")
            template_start = template[0:block_start]
            template_end = template[block_end+19:]
            block = template[block_start:block_end]

            result_aggregation = template_start

            for measure in current:

                name = measure.name
                if measure.name in props:
                    name = props[measure.name]

                middle = block.replace("{name}", name).\
                    replace("{temperature}", str(measure.temperature)).\
                    replace("{humidity}", str(measure.humidity)).\
                    replace("{timestamp}", str(measure.timestamp)[:-7])
                result_aggregation = result_aggregation + middle

            result_aggregation = result_aggregation + template_end
            self.wfile.write(bytes(result_aggregation, "utf-8"))

    def handle_rest_service_call(self):
        props = load_properties("./deviceNames.properties")
        current = Measures().get_current_measures()

        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()

        self.wfile.write(bytes("{\n\"measures\" : [ \n", "utf-8"))

        is_first = True

        for measure in current:

            name = measure.name
            if measure.name in props:
                name = props[measure.name]

            if not is_first:
                self.wfile.write(bytes(",\n", "utf-8"))
            is_first = False

            self.wfile.write(bytes("{\n\"name\" : \"%s\"\n" % name, "utf-8"))
            self.wfile.write(bytes("\"temperature\" : \"%s\"\n" % str(measure.temperature), "utf-8"))
            self.wfile.write(bytes("\"humidity\" : \"%s\"\n" % str(measure.humidity), "utf-8"))
            self.wfile.write(
                bytes("\"timestamp\" : \"%s\"\n}\n" % measure.timestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)"), "utf-8"))

        self.wfile.write(bytes("]\n}", "utf-8"))


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


class MeasuresServer(object):
    webserver = None
    running = False

    def __init__(self, hostname, server_port):
        self.webserver = ThreadingSimpleServer((hostname, server_port), MeasuresServerHandler)
        LOG.info("Webserver prepared on hostname " + hostname + " and port " + str(server_port))

    def run_server_async(self):
        daemon = threading.Thread(target=self.run_server)
        daemon.setDaemon(True)
        daemon.start()
        LOG.info("Starting Webserver ")

    def run_server(self):
        self.running = True
        while self.running:
            self.webserver.handle_request()
            LOG.info("Webserver served request")

    def stop_server(self):
        self.running = False
        LOG.info("Webserver set to stop")


def load_properties(filepath, sep='=', comment_char='#'):
    """
    Read the file passed as parameter as a properties file.
    """
    props = {}
    with open(filepath, "rt") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):
                key_value = l.split(sep)
                key = key_value[0].strip()
                value = sep.join(key_value[1:]).strip().strip('"')
                props[key] = value
    return props
