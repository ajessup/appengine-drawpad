#!/usr/bin/env python

from models import Path

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util
from google.appengine.ext import db

import os

class IndexHandler(webapp.RequestHandler):
	def get(self):
		"""
		Directory of all drawings stored in the data store
		"""
		q = Path.all()
		q.order("-date_created")
		template_values = {
			'drawings': q,
		}
		path = os.path.join(os.path.dirname(__file__), 'templates/admin.html')
		self.response.out.write(template.render(path, template_values))

class ThumbnailHandler(webapp.RequestHandler):
	def get(self):
		"""
		Render the thumbnail of a drawing and render a PNG
		"""
		drawing_id = self.request.get('drawing_id')
		path = Path.get(db.Key(drawing_id))
		self.response.headers['Content-Type'] = 'image/png'
		self.response.out.write(path.generate_preview_png())

class DeleteHandler(webapp.RequestHandler):
	def get(self):
		"""
		Delete a drawing
		"""
		drawing_id = self.request.get('drawing_id')
		path = Path.get(db.Key(drawing_id))
		path.delete()
		self.redirect('/admin/')

def main():
	application = webapp.WSGIApplication([('/admin/', IndexHandler),
										  ('/admin/thumbnail', ThumbnailHandler),
										  ('/admin/delete', DeleteHandler),
										 ],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()