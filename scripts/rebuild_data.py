"""Rebuild local APS boundary/address datasets for the school boundary map.

This script uses only the Python standard library. It downloads Arlington GIS
Open Data GeoJSON files, filters the target school boundaries, spatially joins
address points to the target area, and writes the local files consumed by
index.html.
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

SCHOOL_BOUNDARY_ITEM = "77e4810beb2b49d5bc3bb79bc8b4218c"
ADDRESS_POINTS_ITEM = "7cb763ea99d246f19fa5d5642c928783"

DOWNLOADS = {
    "middle_all.geojson": (
        "https://gisdata-arlgis.opendata.arcgis.com/api/download/v1/items/"
        f"{SCHOOL_BOUNDARY_ITEM}/geojson?layers=1"
    ),
    "high_all.geojson": (
        "https://gisdata-arlgis.opendata.arcgis.com/api/download/v1/items/"
        f"{SCHOOL_BOUNDARY_ITEM}/geojson?layers=2"
    ),
    "address_points_all.geojson": (
        "https://gisdata-arlgis.opendata.arcgis.com/api/download/v1/items/"
        f"{ADDRESS_POINTS_ITEM}/geojson?layers=0"
    ),
}


def download_file(url: str, path: Path) -> None:
    print(f"Downloading {path.name}...")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=240) as response:
        path.write_bytes(response.read())


def load_geojson(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def point_in_ring(point: tuple[float, float], ring: list[list[float]]) -> bool:
    x, y = point
    inside = False
    j = len(ring) - 1
    for i, current in enumerate(ring):
        xi, yi = current[0], current[1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y):
            x_at_y = (xj - xi) * (y - yi) / (yj - yi + 1e-30) + xi
            if x < x_at_y:
                inside = not inside
        j = i
    return inside


def point_in_polygon(point: tuple[float, float], polygon: list[list[list[float]]]) -> bool:
    if not polygon or not point_in_ring(point, polygon[0]):
        return False
    return not any(point_in_ring(point, hole) for hole in polygon[1:])


def point_in_feature(point: tuple[float, float], feature: dict) -> bool:
    geometry = feature.get("geometry") or {}
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates") or []
    if geometry_type == "Polygon":
        return point_in_polygon(point, coordinates)
    if geometry_type == "MultiPolygon":
        return any(point_in_polygon(point, polygon) for polygon in coordinates)
    return False


def build_outputs() -> tuple[int, dict[str, int]]:
    middle = load_geojson(DATA_DIR / "middle_all.geojson")
    high = load_geojson(DATA_DIR / "high_all.geojson")
    addresses = load_geojson(DATA_DIR / "address_points_all.geojson")

    selected_middle = [
        feature
        for feature in middle["features"]
        if "Dorothy Hamm" in feature["properties"].get("MS_Name", "")
        or "Williamsburg" in feature["properties"].get("MS_Name", "")
    ]
    yorktown = next(
        feature
        for feature in high["features"]
        if "Yorktown" in feature["properties"].get("HS_Name", "")
    )

    counts: dict[str, int] = {
        "Dorothy Hamm Middle School": 0,
        "Williamsburg Middle School": 0,
    }
    qualified = []
    keep = [
        "OBJECTID",
        "FULL_ADDRESS",
        "UNITCOUNT",
        "ZIP5",
        "CITY",
        "STATE",
        "STATUS",
        "ADDRESS_TYPE",
        "APS_ELIGIBLE",
        "Middle_School",
        "High_School",
    ]

    for feature in addresses["features"]:
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        if geometry.get("type") != "Point" or len(coordinates) < 2:
            continue

        point = (coordinates[0], coordinates[1])
        if not point_in_feature(point, yorktown):
            continue

        middle_match = None
        for middle_feature in selected_middle:
            if point_in_feature(point, middle_feature):
                middle_match = middle_feature["properties"]["MS_Name"]
                break

        if not middle_match:
            continue

        properties = feature["properties"].copy()
        properties["Middle_School"] = middle_match
        properties["High_School"] = "Yorktown High School"
        qualified.append(
            {
                "type": "Feature",
                "properties": {key: properties.get(key) for key in keep},
                "geometry": geometry,
            }
        )
        counts[middle_match] = counts.get(middle_match, 0) + 1

    selected_boundaries = {
        "type": "FeatureCollection",
        "features": selected_middle + [yorktown],
    }
    qualified_geojson = {"type": "FeatureCollection", "features": qualified}

    (DATA_DIR / "selected_boundaries.geojson").write_text(
        json.dumps(selected_boundaries, separators=(",", ":")),
        encoding="utf-8",
    )
    (DATA_DIR / "qualified_addresses.geojson").write_text(
        json.dumps(qualified_geojson, separators=(",", ":")),
        encoding="utf-8",
    )
    (DATA_DIR / "school_data.js").write_text(
        "window.SCHOOL_BOUNDARIES="
        + json.dumps(selected_boundaries, separators=(",", ":"))
        + ";\nwindow.QUALIFIED_ADDRESSES="
        + json.dumps(qualified_geojson, separators=(",", ":"))
        + ";\nwindow.QUALIFIED_COUNTS="
        + json.dumps(counts, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    csv_fields = [
        "FULL_ADDRESS",
        "Middle_School",
        "High_School",
        "UNITCOUNT",
        "ZIP5",
        "CITY",
        "STATE",
        "STATUS",
        "ADDRESS_TYPE",
        "OBJECTID",
        "Longitude",
        "Latitude",
    ]
    with (DATA_DIR / "qualified_addresses.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=csv_fields)
        writer.writeheader()
        for feature in qualified:
            properties = feature["properties"].copy()
            properties["Longitude"] = feature["geometry"]["coordinates"][0]
            properties["Latitude"] = feature["geometry"]["coordinates"][1]
            writer.writerow({key: properties.get(key) for key in csv_fields})

    return len(qualified), counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Use existing files in data/ instead of downloading fresh source GeoJSON.",
    )
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not args.skip_download:
        for filename, url in DOWNLOADS.items():
            download_file(url, DATA_DIR / filename)

    total, counts = build_outputs()
    print(f"Qualified addresses: {total:,}")
    for name, count in counts.items():
        print(f"{name}: {count:,}")


if __name__ == "__main__":
    main()
