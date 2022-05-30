#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from unittest import result
import dateutil.parser
import babel
from flask_moment import Moment
from flask import Flask, render_template, request, Response, flash, redirect, abort, url_for, jsonify
from model import *
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from wtforms import BooleanField
from logging import FileHandler, WARNING
from werkzeug.wrappers import Request, Response
import pytest
import sys


@app.route('/')
def index():
    currentVenues = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
    currentArtists = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
    return render_template('pages/home.html', venues=currentVenues, artists=currentArtists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    venue_areas = db.session.query(Venue.city, Venue.state).group_by(Venue.state,
                                                                     Venue.city).all()
    data = []

    for area in venue_areas:
        venues = db.session.query(Venue.id, Venue.name).filter(
            Venue.city == area[0], Venue.state == area[1]).all()
        data.append({
            'city': area.city,
            'state': area.state,
            'venues': []
        })
        for venue in venues:
            data[-1]['venues'].append({
                'id': venue[0],
                'name': venue[1]
            })

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response={
    'count': len(results),
    'data': []
    }
  for venue in results:
    response['data'].append({
        'id': venue.id,
        'name': venue.name
      })
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # venue = Venue.query.all()[0]
    venue = Venue.query.get(venue_id)
    setattr(venue, "genres", venue.genres.split(',')) 
  
    # dispaly past shows
    # past_shows = list(filter(lambda show: show.start_time < datetime.now(), venue.shows))
    past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==venue_id).filter(Show.start_time<datetime.now()).all() 
    venue_shows = []
    for show in past_shows:
        show_details = {}
        show_details['artist_name'] = show.artist.name
        show_details['artist_id'] = show.artist.id
        show_details['artist_image_link'] = show.artist.image_link
        show_details['start_time'] = str(show.start_time)
        venue_shows.append(show_details)

    setattr(venue, 'past_shows', venue_shows)
    setattr(venue,'past_shows_count', len(past_shows))

    # display shows
    # upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), venue.shows))
    
    upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==venue_id).filter(Show. start_time>datetime.now()).all()  
    venue_shows = []
    for show in upcoming_shows:
        show_details  = {}
        show_details ['artist_name'] = show.artist.name
        show_details ['artist_id'] = show.artist.id
        show_details ['artist_image_link'] = show.artist.image_link
        show_details ['start_time'] = str(show.start_time)
        venue_shows.append(show_details)

    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  create_venue = Venue()
  
  if Request.method == 'POST':
    print(
      request.form.get('seeking_talent'))
    print(
      request.form.get('genres'))
  
  create_venue.name = request.form['name']
  create_venue.city = request.form['city']
  create_venue.state = request.form['state']
  create_venue.address = request.form['address']
  create_venue.phone = request.form['phone']
  create_venue.facebook_link = request.form['facebook_link']
  # create_venue.genres = request.form['genres']
  create_venue.genres = request.form.getlist('genres')
  create_venue.website_link = request.form['website_link']
  create_venue.image_link = request.form['image_link']
  create_venue.seeking_talent = request.form.get(True)
  
  create_venue.seeking_description = request.form['seeking_description']
  try:
    db.session.add(create_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
# Get the url 
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue_details={
    'id': venue.id,
    'name': venue.name,
    'city': venue.city,
     'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'genres': venue.genres,
    'facebook_link': venue.facebook_link,
    'image_link': venue.image_link,
    'website_link': venue.website_link,
    'seeking_description': venue.seeking_description
   
  }
    
    return render_template('forms/edit_venue.html', form=form, venue=venue_details)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
# Update existing Table entry
  venue = Venue.query.get(venue_id)
  
  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  # venue.genres = request.form['genres']
  venue.genres = request.form.getlist('genres')
  venue.facebook_link = request.form['facebook_link']
  venue.image_link = request.form['image_link']
  venue.website_link = request.form['website_link']
  venue.seeking_talent = request.form.get(True)
  venue.seeking_description = request.form['seeking_description']
 
  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('Venue was not Updated successfully!')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venueId = Venue.query.get(venue_id)
        db.session.delete(venueId)
        db.session.commit()
        flash('Venue ' + venueId.name + ' was deleted successfully!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Venue was not deleted successfully.' + venueId.name)
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    data = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()

  response={
    'count': len(results),
    'data': []
  }
  for artist in results:
    response['data'].append({
      'id': artist.id,
      'name': artist.name
      })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    # artist = Venue.query.all()[0]
    artist = Artist.query.get(artist_id)
    setattr(artist, 'genres', artist.genres.split(','))

    # display past shows
    # past_shows = list(filter(lambda show: show.start_time < datetime.now(), artist.shows))
    past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()   
    artist_shows = []
    for show in past_shows:
        show_detais = {}
        show_detais["venue_name"] = show.venue.name
        show_detais["venue_id"] = show.venue.id
        show_detais["venue_image_link"] = show.venue.image_link
        show_detais["start_time"] = str(show.start_time)

        artist_shows.append(show_detais)

    setattr(artist, "past_shows", artist_shows)
    setattr(artist, "past_shows_count", len(past_shows))


    # display upcoming shows
    # upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), artist.shows))
    
    upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all() 
    artist_shows = []
    for show in upcoming_shows:
        show_detais = {}
        show_detais["venue_name"] = show.venue.name
        show_detais["venue_id"] = show.venue.id
        show_detais["venue_image_link"] = show.venue.image_link
        show_detais["start_time"] = str(show.start_time)

        artist_shows.append(show_detais)

    setattr(artist, "upcoming_shows", artist_shows)
    setattr(artist, "upcoming_shows_count", len(upcoming_shows))

    return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # Get the url 
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist_details={
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
     'state': artist.state,
    'phone': artist.phone,
     'genres': artist.genres,
    'facebook_link': artist.facebook_link,
    'image_link': artist.image_link,
    'website_link': artist.website_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description
   
  }
    
    return render_template('forms/edit_artist.html', form=form, artist=artist_details)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
# Update existing Table entry
  artist = Artist.query.get(artist_id)
  
  if Request.method == 'POST':
    print(request.form.get('seeking_venue'))
  
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  # artist.genres = request.form['genres']
  artist.genres = request.form.getlist('genres')
  artist.facebook_link = request.form['facebook_link']
  artist.image_link = request.form['image_link']
  artist.website_link = request.form['website_link']
  artist.seeking_venue = request.form.get(True)
  artist.seeking_description = request.form['seeking_description']
 
  try:
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash("Artist was not Updated successfully!")
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

# end for Artist Upadte 


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  create_artist = Artist()
  create_artist.name = request.form['name']
  create_artist.city = request.form['city']
  create_artist.state = request.form['state']
  # create_artist.genres = request.form['genres']
  create_artist.genres = request.form.getlist('genres')
  create_artist.phone = request.form['phone']
  create_artist.facebook_link = request.form['facebook_link']
  create_artist.image_link = request.form['image_link']
  create_artist.seeking_venue = request.form.get(True)
  create_artist.website_link = request.form['website_link']
  create_artist.seeking_description = request.form['seeking_description']
  try:
    db.session.add(create_artist)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return redirect(url_for('index'))


@app.route("/artists/<artist_id>/delete", methods=["GET"])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        artistId = Artist.query.get(artist_id)
        db.session.delete(artistId)
        db.session.commit()
        flash('Artist ' + artistId.name + ' was deleted successfully!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Artist was not deleted successfully.' + artistId.name)
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("index"))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  show_ref = Show.query.all()
  data = []
  for show in show_ref:
    if(show):
      data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time':show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    
    if form.validate():
        try:
            new_show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(new_show)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            db.session.rollback()
            flash('Show could not be listed!')
        finally:
            db.session.close()
    else:
        print(form.errors)
        flash('Show was not successfully listed.')

    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
