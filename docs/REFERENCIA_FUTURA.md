# APS Yorktown + Dorothy Hamm/Williamsburg - Referencia futura

## Objetivo

Construir una herramienta para identificar direcciones/casas que cumplen esta condicion:

- High School: Yorktown High School
- Middle School: Dorothy Hamm Middle School o Williamsburg Middle School

La version util no se basa en recortes de PDF. Usa datos GIS oficiales de Arlington/APS y puntos oficiales de direcciones.

## Resultado actual

Ultima reconstruccion local: 2026-05-09.

- Total de direcciones que cumplen: 11,045
- Dorothy Hamm Middle School + Yorktown High School: 3,412
- Williamsburg Middle School + Yorktown High School: 7,633

Archivos principales:

- `index.html`: app interactiva con Leaflet.
- `data/school_data.js`: datos embebidos que consume la app.
- `data/qualified_addresses.csv`: tabla exportable de direcciones que cumplen.
- `data/qualified_addresses.geojson`: puntos de direcciones que cumplen.
- `data/selected_boundaries.geojson`: limites seleccionados: Yorktown, Dorothy Hamm, Williamsburg.
- `scripts/rebuild_data.py`: script reproducible para regenerar los datos.

## Fuentes

### School Boundary Polygons

ArcGIS item:

`77e4810beb2b49d5bc3bb79bc8b4218c`

Capas usadas:

- `layers=1`: Middle School Boundary
- `layers=2`: High School Boundary

URLs:

```text
https://gisdata-arlgis.opendata.arcgis.com/api/download/v1/items/77e4810beb2b49d5bc3bb79bc8b4218c/geojson?layers=1
https://gisdata-arlgis.opendata.arcgis.com/api/download/v1/items/77e4810beb2b49d5bc3bb79bc8b4218c/geojson?layers=2
```

### Address Points

ArcGIS item:

`7cb763ea99d246f19fa5d5642c928783`

Capas usadas:

- `layers=0`: Address Point

URL:

```text
https://gisdata-arlgis.opendata.arcgis.com/api/download/v1/items/7cb763ea99d246f19fa5d5642c928783/geojson?layers=0
```

### Referencias visuales

Los PDFs originales se mantienen como referencia visual, no como fuente computacional principal:

- `C:\Users\HP\Downloads\HS_Boundaries_LgFormat_SY25_26.pdf`
- `C:\Users\HP\Downloads\MS_Boundaries_LgFormat_SY25_26.pdf`

## Metodo

1. Descargar limites de middle school y high school desde Arlington GIS Open Data.
2. Descargar todos los address points oficiales de Arlington.
3. Filtrar los limites escolares:
   - Middle: nombres que contienen `Dorothy Hamm` o `Williamsburg`.
   - High: nombre que contiene `Yorktown`.
4. Para cada address point:
   - verificar si el punto cae dentro del poligono de Yorktown;
   - verificar si el punto cae dentro de Dorothy Hamm o Williamsburg;
   - si ambas condiciones son verdaderas, conservar la direccion.
5. Exportar:
   - GeoJSON de direcciones calificadas;
   - CSV de direcciones calificadas;
   - bundle JS para que `index.html` cargue rapido sin CORS.

## Como correr la app

Desde PowerShell:

```powershell
cd C:\Users\HP\Downloads\school_boundary_map
python -m http.server 8771
```

Luego abrir:

```text
http://127.0.0.1:8771/
```

La app usa Leaflet, OpenStreetMap y Turf desde CDN. Para cargar el mapa base y esas librerias, necesita internet. Los datos procesados estan locales.

## Como regenerar los datos

Desde PowerShell:

```powershell
cd C:\Users\HP\Downloads\school_boundary_map
python scripts\rebuild_data.py
```

Para recalcular usando los GeoJSON fuente ya descargados:

```powershell
python scripts\rebuild_data.py --skip-download
```

El script reescribe:

- `data/selected_boundaries.geojson`
- `data/qualified_addresses.geojson`
- `data/qualified_addresses.csv`
- `data/school_data.js`

## Validacion recomendada

Despues de regenerar:

1. Abrir `http://127.0.0.1:8771/`.
2. Confirmar que aparecen los conteos.
3. Probar filtros:
   - `Todas`
   - `Dorothy`
   - `Williamsburg`
4. Buscar una calle conocida, por ejemplo `ROOSEVELT`.
5. Probar una direccion en la caja `Verificar otra direccion`.
6. Confirmar casos puntuales contra el locator oficial de APS:

```text
https://arlgis.maps.arcgis.com/apps/instant/lookup/index.html?appid=fcbef7f2d50c4b2bae5558ae51cb5c14
```

## Limitaciones y cautelas

- El CSV lista address points oficiales, no necesariamente propiedades inmobiliarias normalizadas por unidad fiscal.
- `UNITCOUNT` indica cantidad de unidades cuando la fuente la provee; un punto puede representar mas de una unidad.
- Las capas descargadas desde Open Data pueden tener atributos historicos de `School_Year`. Si APS cambia limites para un nuevo ciclo escolar, hay que comparar contra el locator oficial y los PDFs vigentes.
- El endpoint REST `query` de algunas capas APS dio timeouts o errores 500/503 durante el desarrollo. La descarga masiva por ArcGIS Hub funciono mejor y por eso se usa en `scripts/rebuild_data.py`.
- Para decisiones de compra/alquiler o matricula, validar siempre la direccion final en el locator oficial de APS.

## Artefactos heredados

Estos archivos son de la fase inicial basada en PDFs y se conservan solo como respaldo visual:

- `APS_target_zones_only.png`
- `APS_Yorktown_DHMS_Williamsburg_compare.png`
- `candidate_*.png`
- `hs_*_crop.png`
- `ms_*_crop.png`
- `assets/focus_*.png`
- `assets/hs_yorktown_source.png`
- `assets/ms_dhms_williamsburg_source.png`

La app actual usa `index.html` y los archivos dentro de `data/`.
