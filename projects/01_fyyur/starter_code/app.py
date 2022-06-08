#----------------------------------------------------------------------------#

# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import collections
collections.Callable = collections.abc.Callable
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:chidera@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
 
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  try:
    data = Venue.query.all()
  except Exception as error:
    data = None
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  user_to_search = request.form.get('search_term')
  x = db.session.query(Venue).with_entities(Venue.id, Venue.name).filter(Venue.name.ilike('%' + user_to_search + '%')).all()
  data = []
  for i in x:
    data.append({
      'id': i.id,
      'name': i.name
    })
  response = {
    'count': len(x),
    'data': data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  x = Venue.query.get(venue_id)
  data = {
    "id": x.id,
    "name": x.name,
    "genres": x.genres,
    "city": x.city,
    "address": x.address,
    "state": x.state,
    "phone": x.phone,
    "website_link": x.website_link,
    "facebook_link": x.facebook_link,
    "seeking_venue": x.seeking_venue,
    "seeking_description": x.seeking_description,
    "image_link": x.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.Venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "artist_id": show.Artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  data['show'] = past_shows
  data['show_count'] = len(past_shows)
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.Venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  for shows in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": upcoming_shows.Artist_id,
      "artist_name": upcomming_show.artist.name,
      "artist_image_link": upcomming_show.artist.image_link,
      "start_time": format_datetime(str(upcomming_show.start_time)) 
    })

  data['shows'] = upcoming_shows
  data['shows_count'] = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  try:
    user_to_create = Venue(
    name=form.name.data,
    city=form.city.data,
    state=form.state.data,
    address=form.address.data,
    phone=form.phone.data,
    genres=form.genres.data,
    facebook_link=form.facebook_link.data,
    website_link=form.website_link.data,
    seeking_talent=form.seeking_talent.data,
    seeking_description=form.seeking_description.data)

    db.session.add(user_to_create)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as error:
    flash('Venue ' + request.form['name'] + 'could not be listed')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/{{venue.id}}/delete"', methods=['POST', 'DELETE'])
def delete_venue(venue_id):
  form = VenueForm()
  try:
    user_to_delete = Venue.query.get(venue_id)
    db.session.delete(user_to_delete)
    db.session.commit()
  except Exception as error:
    db.session.rollback()
  finally:
    db.session.close()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  try:
    data = Artist.query.all()
  except Exception:
    data = None
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  user_to_search = request.form.get('search_term')
  x = db.session.query(Artist).with_entities(Artist.id, Artist.name).filter(Artist.name.ilike('%' + user_to_search + '%')).all()
  data = []
  for i in x:
    data.append({
      'id': i.id,
      'name': i.name
    })
    
  response = {
    'count': len(x),
    'data': data
  }
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  x = Artist.query.get(artist_id)
  data = {
    "id": x.id,
    "name": x.name,
    "genres": x.genres,
    "city": x.city,
    "state": x.state,
    "phone": x.phone,
    "website_link": x.website_link,
    "facebook_link": x.facebook_link,
    "seeking_venue": x.seeking_venue,
    "seeking_description": x.seeking_description,
    "image_link": x.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.Artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []
  for show in past_shows_query:
    past_shows.append({
      "venue_id": show.Venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  data['show'] = past_shows
  data['show_count'] = len(past_shows)
  
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.Artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  for shows in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": shows.Venue_id,
      "venue_name": shows.venue.name,
      "venue_image_link": shows.venue.image_link,
      "start_time": format_datetime(str(shows.start_time))
      })

  data['shows'] = upcoming_shows
  data['shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
 
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  try:
    if artist is not None:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist_image_link = form.artist_image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website_link.data = form.website_link.data
      
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully updated!')
  except Exception as error:
      flash('An error occurred. Artist' + form.name.data + 'could not be updated.')
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html',venue=venue,form=form)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  try:
    if venue is not None:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.genres = form.genres.data
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website_link = form.website_link.data
      db.session.commit()

      flash('Artist ' + form.name.data + ' was successfully updated!')
  except Exception as error:
      flash('An error occurred. Artist' + form.name.data + 'could not be updated.')
# TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  try:
    user_to_create = Artist(
    name=form.name.data,
    city=form.city.data,
    state=form.state.data,
    phone=form.phone.data,
    genres=form.genres.data,
    image_link=form.image_link.data,
    facebook_link=form.facebook_link.data,
    website_link=form.website_link.data,
    seeking_venue=form.seeking_venue.data,
    seeking_description=form.seeking_description.data)
    db.session.add(user_to_create)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as error:
    flash('Artist ' + request.form['name'] + ' could not be  listed!')
  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.join(Artist, Artist.id == Show.Artist_id).join(Venue, Venue.id == Show.Venue_id).all()
  response = []
  for show in data:
    response.append({
    "venue_id": show.Venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.Artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)})
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  try:
    Artist_id = db.session.query(Artist).filter_by(id = request.form.get("Artist_id")).first()
    Venue_id = db.session.query(Venue).filter_by(id = request.form.get("Venue_id")).first()
    if Artist_id is not None or Venue_id is not None:
      user_to_create = Show(
      start_time = request.form.get("start_time"),
      Artist_id = request.form.get("Artist_id"),
      Venue_id = request.form.get("Venue_id"))
      db.session.add(user_to_create)
      db.session.commit()
      flash('Show was successfully listed!')
  except Exception as error:
      flash('An error occurred. Show could not be listed.')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.  
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':

  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''