"""
hospitals.py
Finds nearby hospitals using OpenStreetMap's Overpass API.
Includes retry logic and graceful error handling.
"""
from fastapi import APIRouter, Query, HTTPException
import httpx
import math
from app.schemas.schemas import HospitalResponse
from typing import List

router = APIRouter()

def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    """Calculates distance in km between two GPS coordinates."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)

async def query_overpass(lat: float, lon: float, radius: int) -> dict:
    """Queries Overpass API with fallback to backup server."""
    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      node["amenity"="clinic"](around:{radius},{lat},{lon});
      way["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out center;
    """

    servers = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]

    for server in servers:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    server,
                    data={"data": query}
                )
                if response.status_code == 200 and response.content:
                    data = response.json()
                    if "elements" in data:
                        return data
        except Exception as e:
            print(f"Overpass server {server} failed: {e}")
            continue

    return {"elements": []}

@router.get("/nearby", response_model=List[HospitalResponse])
async def get_nearby_hospitals(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    radius: int = Query(5000, description="Search radius in meters")
):
    """Queries OpenStreetMap for hospitals near the given coordinates."""
    try:
        data = await query_overpass(lat, lon, radius)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not fetch hospitals: {str(e)}"
        )

    hospitals = []
    for element in data.get("elements", [])[:20]:
        tags = element.get("tags", {})
        elem_lat = element.get("lat") or element.get("center", {}).get("lat")
        elem_lon = element.get("lon") or element.get("center", {}).get("lon")

        if not elem_lat or not elem_lon:
            continue

        name = tags.get("name") or tags.get("name:en") or "Hospital/Clinic"

        hospitals.append(HospitalResponse(
            hospital_id=str(element.get("id")),
            name=name,
            latitude=elem_lat,
            longitude=elem_lon,
            address=tags.get("addr:full") or tags.get("addr:street", ""),
            phone=tags.get("phone") or tags.get("contact:phone"),
            rating=None,
            specialties=None,
            distance_km=haversine_distance(lat, lon, elem_lat, elem_lon)
        ))

    # Sort by distance
    hospitals.sort(key=lambda h: h.distance_km or 999)
    return hospitals