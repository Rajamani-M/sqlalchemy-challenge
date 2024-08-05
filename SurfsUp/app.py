# Import the dependencies.
import numpy as np
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
                       
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################

def prev_year_date():
    """Calculate the date one year prior to the most recent date in the dataset."""
    most_recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    return most_recent_date - dt.timedelta(days=365)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Climate API! Available Routes!<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23 (start date in yyyy-mm-dd format)<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23 (start and end date in yyyy-mm-dd format)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the last year."""
    one_year_ago = prev_year_date()
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    precipitation_data = [{"date": date, "prcp": prcp} for date, prcp in results]
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station, Station.name).all()
    stations = [{"station": station, "name": name} for station, name in results]
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the last year for the most active station."""
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]
    one_year_ago = prev_year_date()
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()
    tobs_data = [{"date": date, "tobs": tobs} for date, tobs in results]
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return TMIN, TAVG, TMAX from start date to the most recent date."""
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(
        func.min(Measurement.tobs).label("TMIN"),
        func.avg(Measurement.tobs).label("TAVG"),
        func.max(Measurement.tobs).label("TMAX")
    ).filter(Measurement.date >= start_date).all()
    temp_stats = [{"TMIN": min, "TAVG": avg, "TMAX": max} for min, avg, max in results]
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return TMIN, TAVG, TMAX for a date range from start to end date."""
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(
        func.min(Measurement.tobs).label("TMIN"),
        func.avg(Measurement.tobs).label("TAVG"),
        func.max(Measurement.tobs).label("TMAX")
    ).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    temp_stats = [{"TMIN": min, "TAVG": avg, "TMAX": max} for min, avg, max in results]
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
