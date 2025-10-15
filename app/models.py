from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

Base = declarative_base()

class Airline(Base):
    __tablename__ = "airlines"
    carrier = Column(String(7), primary_key=True)
    name = Column(String(100))

class Airport(Base):
    __tablename__ = "airports"
    faa   = Column(String(3), primary_key=True)
    name  = Column(String(100))
    lat   = Column(String(64))    # si ta table est en VARCHAR; sinon change en Float/DECIMAL
    lon   = Column(String(64))
    alt   = Column(String(32))
    tz    = Column(String(8))
    dst   = Column(String(1))
    tzone = Column(String(64))

class Plane(Base):
    __tablename__ = "planes"
    tailnum      = Column(String(7), primary_key=True)
    year         = Column(Integer)
    type         = Column(String(64))
    manufacturer = Column(String(64))
    model        = Column(String(64))
    engines      = Column(Integer)
    seats        = Column(Integer)
    speed        = Column(Integer)
    engine       = Column(String(32))

class Flight(Base):
    __tablename__ = "flights"
    # PK composite dans ta DB : (year, month, day, hour, carrier, flight)
    year   = Column(Integer, primary_key=True)
    month  = Column(Integer, primary_key=True)
    day    = Column(Integer, primary_key=True)
    hour   = Column(Integer, primary_key=True)
    carrier= Column(String(7), ForeignKey("airlines.carrier"), primary_key=True)
    flight = Column(Integer, primary_key=True)

    minute         = Column(Integer)
    dep_time       = Column(String(4))
    sched_dep_time = Column(Integer)
    dep_delay      = Column(Integer)
    arr_time       = Column(String(4))
    sched_arr_time = Column(Integer)
    arr_delay      = Column(Integer)
    tailnum        = Column(String(7), ForeignKey("planes.tailnum"), nullable=True)
    origin         = Column(String(3), ForeignKey("airports.faa"))
    dest           = Column(String(3), ForeignKey("airports.faa"))
    air_time       = Column(Integer)
    distance       = Column(Integer)
    time_hour      = Column(DateTime)