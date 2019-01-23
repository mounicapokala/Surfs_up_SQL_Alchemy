import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask,jsonify

#Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement
session = Session(engine)

#Flask setup
app = Flask(__name__)

#List all routes that are available.
@app.route("/")
def home():
    return (f"Welcome to my Home page! <br/>"
            f"/api/v1.0/precipitation <br/>"
            f"/api/v1.0/stations <br/>"
            f"/api/v1.0/tobs <br/>"
            f"/api/v1.0/&ltstart&gt <br/>"
            f"/api/v1.0/&ltstart&gt/&ltend&gt <br/>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date =  session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_date = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>last_year).\
    order_by(Measurement.date).all()
    prcp_date_dict = {}
    for row in prcp_date:
        prcp_date_dict[row[0]] = row[1]
    return jsonify(prcp_date_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.station, Station.name).all()
    stations_dict = {}
    for row in stations_query:
        stations_dict[row[0]] = row[1]
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def temperature():
    highest_active_station = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).\
                         order_by(func.count(Measurement.tobs).desc()).first()
    active_station_last_date =  session.query(Measurement.date).filter(Measurement.station==highest_active_station.station).\
                                order_by(Measurement.date.desc()).first()
    active_station_last_year = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    temp_active_station = session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.date>active_station_last_year).\
                      filter(Measurement.station==highest_active_station.station).order_by(Measurement.date).all()
    tobs_list = []
    for row in temp_active_station:
        tobs_dict = {}
        tobs_dict["Station"] = temp_active_station[0]
        tobs_dict["Date"] = temp_active_station[1]
        tobs_dict["Temperature"] = temp_active_station[2]
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date_temp(start):
  
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end =  dt.date(2017, 8, 23)
    temp_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end).all()
    start_date_dict = {}
    for row in temp_query:
        start_date_dict["TMin"] = row[0]
        start_date_dict["TAvg"] = row[1]
        start_date_dict["TMax"] = row[2]
    return jsonify(start_date_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start,end):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    start_end_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                      filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    start_end_date_dict = {}
    for row in start_end_query:
        start_end_date_dict["TMin"] = row[0]
        start_end_date_dict["TAvg"] = row[1]
        start_end_date_dict["TMax"] = row[2]
    return jsonify(start_end_date_dict)

if __name__=="__main__":
    app.run(debug=True)