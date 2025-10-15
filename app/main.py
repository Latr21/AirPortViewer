from fastapi import FastAPI, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import func, select, and_
from .models import Airline, Airport, Flight, Plane
from .deps import get_db
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # monte d'un niveau
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app = FastAPI(title="ADP – Trafic aérien")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --------- Pages HTML ---------

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    # KPIs rapides
    total_flights = db.execute(select(func.count()).select_from(Flight)).scalar() or 0
    total_airports = db.execute(select(func.count()).select_from(Airport)).scalar() or 0
    total_airlines = db.execute(select(func.count()).select_from(Airline)).scalar() or 0
    total_planes   = db.execute(select(func.count()).select_from(Plane)).scalar() or 0

    # Top 10 destinations par volume
    top_dest = db.execute(
        select(Flight.dest, func.count().label("cnt"))
        .group_by(Flight.dest)
        .order_by(func.count().desc())
        .limit(10)
    ).all()

    # Top 10 origines (si utile)
    top_origin = db.execute(
        select(Flight.origin, func.count().label("cnt"))
        .group_by(Flight.origin)
        .order_by(func.count().desc())
        .limit(10)
    ).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "kpis": {
                "flights": total_flights,
                "airports": total_airports,
                "airlines": total_airlines,
                "planes": total_planes,
            },
            "top_dest": top_dest,
            "top_origin": top_origin,
        },
    )

@app.get("/airlines", response_class=HTMLResponse)
def list_airlines(
    request: Request,
    q: str | None = Query(None, description="Recherche par nom ou code"),
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    stmt = select(Airline)
    if q:
        like = f"%{q.upper()}%"
        stmt = stmt.where(
            (Airline.carrier.ilike(like)) | (Airline.name.ilike(f"%{q}%"))
        )
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    rows = db.execute(stmt.order_by(Airline.carrier).offset((page-1)*size).limit(size)).scalars().all()
    return templates.TemplateResponse(
        "airlines.html",
        {"request": request, "rows": rows, "q": q or "", "page": page, "size": size, "total": total},
    )

@app.get("/airports", response_class=HTMLResponse)
def list_airports(
    request: Request,
    q: str | None = Query(None, description="Recherche par FAA ou nom"),
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    stmt = select(Airport)
    if q:
        like = f"%{q.upper()}%"
        stmt = stmt.where((Airport.faa.ilike(like)) | (Airport.name.ilike(f"%{q}%")))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    rows = db.execute(stmt.order_by(Airport.faa).offset((page-1)*size).limit(size)).scalars().all()
    return templates.TemplateResponse(
        "airports.html",
        {"request": request, "rows": rows, "q": q or "", "page": page, "size": size, "total": total},
    )

@app.get("/flights", response_class=HTMLResponse)
def list_flights(
    request: Request,
    carrier: str | None = Query(None),
    origin: str | None = Query(None),
    dest: str | None = Query(None),
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_db),
):
    filters = []
    if carrier:
        filters.append(Flight.carrier == carrier.upper().strip())
    if origin:
        filters.append(Flight.origin == origin.upper().strip())
    if dest:
        filters.append(Flight.dest == dest.upper().strip())

    stmt = select(
        Flight.year, Flight.month, Flight.day,
        Flight.hour, Flight.carrier, Flight.flight,
        Flight.origin, Flight.dest, Flight.dep_delay, Flight.arr_delay, Flight.distance
    )
    if filters:
        stmt = stmt.where(and_(*filters))

    # pagination
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    rows = db.execute(
        stmt.order_by(Flight.year, Flight.month, Flight.day, Flight.hour, Flight.carrier, Flight.flight)
            .offset((page-1)*size).limit(size)
    ).all()

    # pour remplir les select distinct des filtres
    carriers = db.execute(select(Airline.carrier).order_by(Airline.carrier)).scalars().all()
    origins  = db.execute(select(Airport.faa).order_by(Airport.faa)).scalars().all()
    dests    = origins  # mêmes codes

    return templates.TemplateResponse(
        "flights.html",
        {
            "request": request,
            "rows": rows,
            "carrier": carrier or "",
            "origin": origin or "",
            "dest": dest or "",
            "carriers": carriers,
            "origins": origins,
            "dests": dests,
            "page": page,
            "size": size,
            "total": total,
        },
    )

# --------- API JSON minimal ---------

@app.get("/api/kpis")
def api_kpis(db: Session = Depends(get_db)):
    return {
        "flights": db.execute(select(func.count()).select_from(Flight)).scalar() or 0,
        "airports": db.execute(select(func.count()).select_from(Airport)).scalar() or 0,
        "airlines": db.execute(select(func.count()).select_from(Airline)).scalar() or 0,
        "planes": db.execute(select(func.count()).select_from(Plane)).scalar() or 0,
    }