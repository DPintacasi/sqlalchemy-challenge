import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#---------------
#database set up 
#---------------

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#---------------
#app set up
#---------------

app = Flask(__name__)

#---------------
#routes 
#---------------


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start_date</br>"
        f"/api/v1.0/start_date/end_date</br>"
        f"Date formart YYYY-MM-DD"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return a list of all the precipitation measurements in a distionary with date as key"""

    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    prcp = {}
    for row in results:
        prcp[row[0]] = row[1]   
    

    return jsonify(prcp)



@app.route("/api/v1.0/stations")
def stations():

    """Return a list of all stations names"""

    session = Session(engine)

    results = session.query(Station.name).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def temperatures():

    """Return a list of all temps in the last year taken from more active station names"""

    session = Session(engine)
    
    #find most active station
    active_stations = session.query(Measurement.station,func.count(Measurement.id)).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.id).desc()).first()
    most_active = active_stations[0]

    #calculate date for one year ago
    most_recent = session.query(func.max(Measurement.date)).first()
    one_year_ago = dt.datetime.strptime(most_recent[0], '%Y-%m-%d') - dt.timedelta(days = 365)

    #final temp query
    results = session.query(Measurement.tobs).\
                filter(Measurement.station == most_active).\
                filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    all_temps = list(np.ravel(results))

    return jsonify(all_temps)



@app.route("/api/v1.0/<start>")
def from_startdate(start):

    """Return min, max, and average temp for range from start date till most recent"""

    session = Session(engine)

    sel = func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)
    results = session.query(* sel).filter(Measurement.date >= start).first()

    session.close()
    
    temps = {'min_temp' : results[0],
                    'avg_temp': round(results[1],2),
                    'max_temp' : results[2]}

    return jsonify(temps)



@app.route("/api/v1.0/<start>/<end>")
def temp_in_date_range(start,end):

    """Return min, max, and average temp for range from start date till end date"""

    session = Session(engine)

    sel = func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)
    results = session.query(* sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).first()

    session.close()
    
    temps = {'min_temp' : results[0],
                    'avg_temp': round(results[1],2),
                    'max_temp' : results[2]}

    return jsonify(temps)


#-----------
#Run app
#-----------

if __name__ == "__main__":
    app.run(debug=True)

