#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os, cgi, logging, datetime, md5

from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.ext import db

from models import Path

class IndexHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, None))

class DrawHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/draw.html')
        self.response.out.write(template.render(path, None))

class DataHandler(webapp.RequestHandler):
    def post(self):
        logging.info("Data POST Starting...")
        data = json.loads(self.request.body)   
        paths = json.dumps(data['paths'])
        if len(paths) > 400:
            json_hash = md5.new(str(paths)[400]).hexdigest()
        else:
            json_hash = md5.new(str(paths)).hexdigest()
        logging.info("Storing: %s - %s" % (json_hash, paths))
        stored_path = Path(key_name = json_hash, json=paths)
        stored_path.put()
        self.response.out.write('{ "success" : "ok" }')   
 
    def get(self):
        drawing_id = self.request.get('drawing_id', default_value=None)
        logging.info("Data GET Starting (%s)..." % drawing_id)
        if drawing_id is None:
            q = Path.all()
            q.order("play_count")
            path = q.fetch(1)[0]
        else:
            path = Path.get(db.Key(drawing_id))
        path.play_count = path.play_count + 1
        path.put()
        self.response.out.write('[{"paths":'+path.json+',"success":true}]')

def main():
    application = webapp.WSGIApplication([('/', IndexHandler),
                                          ('/draw', DrawHandler),
                                          ('/data.json', DataHandler),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
