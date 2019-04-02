import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import datetime as dt
from datetime import timedelta
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
session_factory = sessionmaker(bind=engine)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = scoped_session(session_factory)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href=\"/api/v1.0/precipitation\">Precipitation Data</a><br/>"
        f"<a href=\"/api/v1.0/stations\">Station Names</a><br/>"
        f"<a href=\"/api/v1.0/tobs\">Last year temps in DB</a><br/>"
        f"<a href=\"/api/v1.0/average-temp-calculator?startDate=2016-01-01&endDate=2016-05-01\">Average temp calculator for given dates</a><br/>"
    )
@app.route("/api/v1.0/average-temp-calculator")
def avgtempcalc():
    #returns TMIN`, `TAVG`, and `TMAX` for a given date range (passed in query string) 
    startDate =dt.datetime.strptime(request.args.get('startDate'),'%Y-%m-%d' ) 
    endDate =dt.datetime.strptime(request.args.get('endDate'),'%Y-%m-%d' )
    tempsData = session.query(Measurement.tobs).filter(Measurement.date > startDate).\
        filter(Measurement.date < endDate).all()
    results = "The minimum temp is "+ str(min(tempsData))+" and the maximum is "+ str(max(tempsData) )
    return results


@app.route("/api/v1.0/tobs")
def tobs():
     #Getting the last date recorded in the database
    lastRecordedDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #Convert the date from string to a datetime type
    lastRecordedDate = dt.datetime.strptime(lastRecordedDate[0],'%Y-%m-%d' )
    #Going back 12 months before that date
    yearBeforelastRecordedDate = lastRecordedDate  - relativedelta(months=+12)
    #Now we have the dates to query between. Lets get the temps between those dates
    tempsData = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date > yearBeforelastRecordedDate).all()
    return jsonify(tempsData)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results

    #Getting the last date recorded in the database
    lastRecordedDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #Convert the date from string to a datetime type
    lastRecordedDate = dt.datetime.strptime(lastRecordedDate[0],'%Y-%m-%d' )
    #Going back 12 months before that date
    yearBeforelastRecordedDate = lastRecordedDate  - relativedelta(months=+12)
    #Now we have the dates to query between. Lets get the precipitation between those dates
    precipitationData = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date > yearBeforelastRecordedDate).all()
    
    return jsonify(precipitationData)
    


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all station names in the database"""
    # Query all stations
    stations = session.query(Station.name).all()

    return jsonify(stations)


if __name__ == '__main__':
    app.run(debug=True)
