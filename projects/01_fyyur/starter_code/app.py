#----------------------------------------------------------------------------#

# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import collections
import sys
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
db.init_app(app)
migrate = Migrate(app, db)



 
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
  data = Venue.query.all()
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  user_to_search = request.form.get('search_term')
  x = db.session.query(Venue).with_entities(Venue.id, Venue.name).filter(
      Venue.name.ilike(f'%{user_to_search}%')).all()
  data = [{'id': i.id, 'name': i.name} for i in x]
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
  
  past_shows = [{
       "artist_id": show.Artist_id,
       "artist_name": show.artist.name,
       "artist_image_link": show.artist.image_link,
       "start_time": format_datetime(str(show.start_time))} for show in past_shows_query]

  data['show'] = past_shows
  data['show_count'] = len(past_shows)

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.Venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = [{
      "artist_id": upcoming_shows.Artist_id,
      "artist_name": upcomming_show.artist.name,
      "artist_image_link": upcomming_show.artist.image_link,
      "start_time": format_datetime(str(upcomming_show.start_time))} for shows in upcoming_shows_query]

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
  form = ArtistForm
  error = False
  try:
    user_to_create = Venue(name = request.form.get('name'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    address = request.form.get('address'),
    phone = request.form.get('phone'),
    genres = request.form.get('genres'),
    image_link = request.form.get('image_link'),
    facebook_link = request.form.get('facebook_link'),
    website_link = request.form.get('website_link'),
    seeking_talent = request.form.get('seeking_talent').lower() == 'true',
    seeking_description = request.form.get('seeking_description'))
    db.session.add(user_to_create)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('Venue ' + request.form['name'] + ' could not be  listed!')
  finally:
    db.session.close()
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
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  user_to_search = request.form.get('search_term')
  x = db.session.query(Artist).with_entities(Artist.id, Artist.name).filter(Artist.name.ilike(f'%{user_to_search}%')).all()  
  data = [{'id': i.id, 'name': i.name} for i in x]
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
  past_shows = [{
       "venue_id": show.Venue_id,
       "venue_name": show.venue.name,
       "venue_image_link": show.venue.image_link,
       "start_time": format_datetime(str(show.start_time)) }  for show in past_shows_query]
  data['show'] = past_shows
  data['show_count'] = len(past_shows)

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.Artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = [{
      "venue_id": shows.Venue_id,
      "venue_name": shows.venue.name,
      "venue_image_link": shows.venue.image_link,
      "start_time": format_datetime(str(shows.start_time))
      }for shows in upcoming_shows_query]

  data['shows'] = upcoming_shows
  data['shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm()
  if artist:
    request.form.get('name') == artist.name
    request.form.get('city') == artist.city
    request.form.get('state') == artist.state
    request.form.get('phone') == artist.phone
    request.form.get('genres') == artist.genres
    request.form.get('image_link') == artist.image_link
    request.form.get('facebook_link') == artist.facebook_link
    request.form.get('website_link') == artist.website_link
    request.form.get('seeking_venue') == artist.seeking_venue
    request.form.get('seeking_description') == artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
 
  form = ArtistForm(request.form)
  try:
    if artist := Artist.query.filter_by(id=artist_id).first():
      artist.name = request.form.get('name')
      artist.city = request.form.get('city')
      artist.state = request.form.get('state')
      artist.phone = request.form.get('phone')
      artist.genres = request.form.get('genres')
      artist_image_link = request.form.get('image_link')
      artist.facebook_link = request.form.get('facebook_link')
      artist.website_link = request.form.get('website_link')
      db.session.commit()
      flash(f'Artist {form.name.data} was successfully updated!')
    
  except Exception as error:
    flash(f'An error occurred {form.name.data} could not be updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  form = VenueForm()
  if venue:
    request.form.get('name') == venue.name
    request.form.get('city') == venue.city
    request.form.get('state') == venue.state
    request.form.get('phone') == venue.phone
    request.form.get('genres') == venue.genres
    request.form.get('image_link') == venue.image_link
    request.form.get('facebook_link') == venue.facebook_link
    request.form.get('website_link') == venue.website_link
    request.form.get('seeking_talent') == venue.seeking_talent
    request.form.get('seeking_description') == venue.seeking_description
  return render_template('forms/edit_venue.html',venue=venue,form=form)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  try:
    if venue := Venue.query.filter_by(id=venue_id).first():
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.phone = request.form.get('phone')
      venue.genres = request.form.get('genres')
      venue.image_link = request.form.get('image_link')
      venue.facebook_link = request.form.get('facebook_link')
      venue.website_link = request.form.get('website_link')
      db.session.commit()
      flash(f'Venue {form.name.data} was successfully updated!')
  except Exception:
    flash(f'An error occurred {form.name.data} could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm
  error = False
  try:
    user_to_create = Artist(name = request.form.get('name'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    genres = request.form.get('genres'),
    image_link = request.form.get('image_link'),
    facebook_link = request.form.get('facebook_link'),
    website_link = request.form.get('website_link'),
    seeking_venue = request.form.get('seeking_venue').lower() == 'true',
    seeking_description = request.form.get('seeking_description'))
    db.session.add(user_to_create)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    flash('Artist ' + request.form['name'] + ' could not be  listed!')
  finally:
    db.session.close()
  return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.join(Artist, Artist.id == Show.Artist_id).join(Venue, Venue.id == Show.Venue_id).all()
  response = [{
    "venue_id": show.Venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.Artist_id,
     "artist_name": show.artist.name,
     "artist_image_link": show.artist.image_link,
     "start_time": str(show.start_time)
      } for show in data]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
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
  except Exception:
      error = True
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
  finally:
   db.session.close()
  
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