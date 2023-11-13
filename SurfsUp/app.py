# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
 # Create a database session object
session = Session(engine)

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    latest_record = session.query(Measurement).order_by(Measurement.date.desc()).first()
    latest_date = latest_record.date
    #format the latest date 
    year_month_day= latest_date.split("-")
    year = int(year_month_day[0])
    month = int(year_month_day[1])
    day  = int(year_month_day[2])

    #calculate the previous year date
    prev_year_date = dt.date(year,month,day) - dt.timedelta(days=365)

    precip_results = session.query(Measurement).filter(Measurement.date >= prev_year_date).all()

    precipitation_data=[]

    for result in precip_results:
         precipitation_dict ={}
         precipitation_dict["id"] = result.id
         precipitation_dict["station"] = result.station
         precipitation_dict["date"] = result.date
         precipitation_dict["prcp"] = result.prcp
         precipitation_dict["tobs"] = result.tobs
         precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)    


@app.route("/api/v1.0/stations")
def stations():
    station_names = session.query(Station.station,Station.name).all()
    station_list = list(np.ravel(station_names))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    latest_record = session.query(Measurement).order_by(Measurement.date.desc()).first()
    latest_date = latest_record.date

    year_month_day= latest_date.split("-")
    year = int(year_month_day[0])
    month = int(year_month_day[1])
    day  = int(year_month_day[2])
    prev_year_date = dt.date(year,month,day) - dt.timedelta(days=365)

    active_stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = active_stations[0][0]
    temp_results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==most_active_station).filter(Measurement.date>=prev_year_date).all()
    
    temp_list = list(np.ravel(temp_results))
    return jsonify(temp_list)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temp = list(np.ravel(results))
        return jsonify(temp)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temp = list(np.ravel(results))
    return jsonify(temp)

if __name__ == '__main__':
    app.run(debug=True)