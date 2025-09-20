#!/usr/bin/env python3
import os
import sys

import geopandas as gpd

SUBBASIN_PATH = (
    "SubBasin_ONWR_WGS84_4K_1A_With_Island/SubBasin_ONWR_WGS84_4K_1A_With_Island.shp"
)
SUBDISTRICT_PATH = "Subdistrict/polbndry_wgs84_z47.shp"


class MergerException(Exception):
    def __init__(self, message, nested_exception=None):
        super().__init__(message)
        self.message = message
        self.nested_exception = nested_exception


def load_shapefiles(subdistrict_path, subbasin_path):
    """Load the sub basin and subdistrict shapefiles."""

    # Check if files exist
    if not os.path.exists(subbasin_path):
        raise MergerException(f"Sub basin shapefile not found: {subbasin_path}")
    if not os.path.exists(subdistrict_path):
        raise MergerException(f"Subdistrict shapefile not found: {subdistrict_path}")

    print("Loading shapefiles...")

    # Load shapefiles
    subbasins = gpd.read_file(subbasin_path, encoding="windows-874")
    subdistricts = gpd.read_file(subdistrict_path, encoding="windows-874")

    print(f"Loaded {len(subbasins)} sub basins")
    print(f"Loaded {len(subdistricts)} subdistricts")

    return subdistricts, subbasins


def ensure_same_crs(gdf1, gdf2):
    """Ensure both GeoDataFrames use the same coordinate reference system."""

    print(f"Subdistrict CRS: {gdf1.crs}")
    print(f"Sub basin CRS: {gdf2.crs}")

    # If CRS are different, transform to WGS84
    if gdf1.crs != gdf2.crs:
        print("Converting to common CRS (WGS84)...")
        gdf1 = gdf1.to_crs("EPSG:4326")
        gdf2 = gdf2.to_crs("EPSG:4326")

    return gdf1, gdf2


def perform_spatial_join_centroid(subdistricts, subbasins):
    """Perform spatial join to find which sub basin each subdistrict is in."""

    print("Performing spatial analysis using subdistrict centroid...")

    # Create centroids of subdistricts for point-in-polygon analysis
    subdistricts_centroids = subdistricts.copy()
    subdistricts_centroids["geometry"] = subdistricts_centroids.geometry.centroid

    # Perform spatial join using centroids
    result = gpd.sjoin(
        subdistricts_centroids, subbasins, how="left", predicate="within"
    )

    return result


def perform_spatial_join_intersect(subdistricts, subbasins):
    """Perform spatial join to find which sub basin each subdistrict is in."""

    print("Performing spatial analysis...")

    # Perform spatial join using centroids
    result = gpd.sjoin(subdistricts, subbasins, how="left", predicate="intersects")

    return result


def create_csv(result, filename):
    # We don't use the polygon stored in 'geometry' column
    df_no_geom = result.drop(columns=["geometry"])
    df_no_geom.to_csv(filename, index=False, encoding="utf-8")


def main():
    try:
        subdistricts, subbasins = load_shapefiles(SUBDISTRICT_PATH, SUBBASIN_PATH)
        subdistricts, subbasins = ensure_same_crs(subdistricts, subbasins)
        result = perform_spatial_join_centroid(subdistricts, subbasins)
        result.to_file("result.shp", encoding="utf-8")
        create_csv(result, "result.csv")
    except MergerException as e:
        print(f"Error: {e.message}")
        sys.exit(-1)


if __name__ == "__main__":
    main()
