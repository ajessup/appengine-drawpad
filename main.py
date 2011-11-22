import os, cgi, logging, datetime, md5

from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util
from google.appengine.ext import db

from models import Path

class IndexHandler(webapp.RequestHandler):
	"""
	Render viewport to be shown on a projector
	"""
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, None))

class DrawHandler(webapp.RequestHandler):
	"""
	Render drawpad (to be shown on an iPhone)
	"""
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/draw.html')
		self.response.out.write(template.render(path, None))

class DataHandler(webapp.RequestHandler):
	"""
	Handle saving and retreiving drawings
	"""
	def post(self):
		data = json.loads(self.request.body)
		try:
			paths = json.dumps(data['paths'])
			key_name = md5.new(str(paths)).hexdigest()
			Path(key_name = key_name, json=paths).put()
			self.response.out.write('{ "success" : "ok" }')	 
		except Exception, e:
			self.response.out.write('{ "error" : %s }' % str(e))	 
 
	def get(self):
		drawing_id = self.request.get('drawing_id', default_value=None)
		if drawing_id is None:
			q = Path.all().order("play_count")
			if q.count():
				path = q.fetch(1)[0]
			else:
				path = Path(key_name='initial',json='{}')
		else:
			path = Path.get(db.Key(drawing_id))
		path.play_count += 1
		path.put()
		self.response.out.write('[{"paths":%s,"success":true}]' % path.json)

def main():
	application = webapp.WSGIApplication([('/', IndexHandler),
										  ('/draw', DrawHandler),
										  ('/data.json', DataHandler),
										 ],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
