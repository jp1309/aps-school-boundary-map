# APS SY2025-26 Boundary Viewer

Interactive map and address dataset for the condition:

Middle School is Dorothy Hamm or Williamsburg, and High School is Yorktown.

Public site:

https://jp1309.github.io/aps-school-boundary-map/

## What It Does

The app uses official Arlington/APS GIS data to identify address points that are inside:

- `Yorktown High School`
- and either `Dorothy Hamm Middle School` or `Williamsburg Middle School`

Current generated result:

- 11,045 qualifying address points
- 3,412 Dorothy Hamm + Yorktown
- 7,633 Williamsburg + Yorktown

## Files

- `index.html`: interactive Leaflet map with official APS boundary polygons, official Arlington address points that meet the condition, local search, map-click checking, and CSV export.
- `docs/REFERENCIA_FUTURA.md`: Spanish project documentation, methodology, refresh instructions, validation steps, and caveats.
- `scripts/rebuild_data.py`: reproducible data rebuild script.
- `data/school_data.js`: local data bundle used by the map.
- `data/qualified_addresses.csv`: address list that meets the condition.
- `data/qualified_addresses.geojson`: address point GeoJSON that meets the condition.
- `data/selected_boundaries.geojson`: Yorktown + Dorothy Hamm + Williamsburg boundary polygons.

## Run Locally

```powershell
python -m http.server 8771
```

Then open:

```text
http://127.0.0.1:8771/
```

## Rebuild Data

Download fresh source data and regenerate all derived files:

```powershell
python scripts\rebuild_data.py
```

Rebuild from already downloaded source GeoJSON files:

```powershell
python scripts\rebuild_data.py --skip-download
```

## Sources

- `School Boundary Polygons`: `https://gisdata-arlgis.opendata.arcgis.com/api/download/v1/items/77e4810beb2b49d5bc3bb79bc8b4218c/geojson`
- `Address Points`: `https://gisdata-arlgis.opendata.arcgis.com/api/download/v1/items/7cb763ea99d246f19fa5d5642c928783/geojson`

For a specific house, verify the final assignment in the official APS Searchable Boundary Locator linked inside the app.
