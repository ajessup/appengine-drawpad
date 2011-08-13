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

import png
from StringIO import StringIO

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
        data = json.loads(self.request.body)
        logging.error("Starting...")
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
        q = Path.all()
        q.order("play_count")
        path = q.fetch(1)[0]
        path.play_count = path.play_count + 1
        path.put()
        self.response.out.write('[{"paths":'+path.json+',"id":178}]')

class Path(db.Model):
    json = db.TextProperty(required=True)
    date_created = db.DateTimeProperty(required=True, auto_now_add=True)
    play_count = db.IntegerProperty(required=True, default=0)

class AdminHandler(webapp.RequestHandler):
    def get(self):
        q = Path.all()
        q.order("-date_created")
        template_values = {
            'drawings': q,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/admin.html')
        self.response.out.write(template.render(path, template_values))

class ThumbnailHandler(webapp.RequestHandler):
    def get(self):
        drawing_id = self.request.get('drawing_id')

        path = Path.get(db.Key(drawing_id))
        paths = json.loads(path.json)
    
        max_x = 0
        max_y = 0

        zoom_factor = 0.25

        # Determine bounds
        for path in paths:
            for point in path:
               if point['x'] > max_x:
                  max_x = point['x']
               if point['y'] > max_y:
                  max_y = point['y']

        max_x = int(max_x * zoom_factor)
        max_y = int(max_y * zoom_factor)

        img_matrix = [[1 for col in range(max_x+1)] for row in range(max_y+1)]
        
        for path in paths:
            for point in path:
               img_matrix[int(point['y']*zoom_factor)][int(point['x']*zoom_factor)] = 0       
    
        f = StringIO()
        w = png.Writer(len(img_matrix[0]), len(img_matrix), greyscale=True, bitdepth=1)
        w.write(f, img_matrix)

        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(f.getvalue())

def main():
    application = webapp.WSGIApplication([('/', IndexHandler),
                                          ('/draw', DrawHandler),
                                          ('/data.json', DataHandler),
                                          ('/thumbnail', ThumbnailHandler),
                                          ('/admin', AdminHandler),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
