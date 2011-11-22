from google.appengine.ext import db

import png
from StringIO import StringIO
from django.utils import simplejson as json

class Path(db.Model):
	"""
	Path model represents a series of points that make up a drawpad drawing
	"""
	
	json = db.TextProperty(required=True)
	date_created = db.DateTimeProperty(required=True, auto_now_add=True)
	play_count = db.IntegerProperty(required=True, default=0)

	PREVIEW_ZOOM_FACTOR = 0.25

	def get_paths(self):
		return json.loads(self.json)

	def generate_preview_png(self):
		paths = self.get_paths()
		max_x = max_y = 0

		# Determine bounds
		for path in paths:
			for point in path:
			   if point['x'] > max_x:
				  max_x = point['x']
			   if point['y'] > max_y:
				  max_y = point['y']

		max_x = int(max_x * self.PREVIEW_ZOOM_FACTOR)
		max_y = int(max_y * self.PREVIEW_ZOOM_FACTOR)

		img_matrix = [[1 for col in range(max_x+1)] for row in range(max_y+1)]
		
		# Create matrix represzenting each point
		for path in paths:
			for point in path:
			   img_matrix[int(point['y']*zoom_factor)][int(point['x']*zoom_factor)] = 0	
				  
		# Convert matrix to PNG
		f = StringIO()
		w = png.Writer(len(img_matrix[0]), len(img_matrix), greyscale=True, bitdepth=1)
		w.write(f, img_matrix)
		
		return f.getvalue()