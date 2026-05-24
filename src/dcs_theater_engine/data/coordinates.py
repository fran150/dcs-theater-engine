"""Coordinate helpers for DCS theater data."""

from __future__ import annotations

from dataclasses import dataclass

from pyproj import CRS, Transformer


@dataclass(frozen=True, slots=True)
class DcsPoint:
    """A point in DCS world coordinates, in meters."""

    x: float
    y: float


@dataclass(frozen=True, slots=True)
class LatLon:
    """A WGS84 latitude/longitude point in decimal degrees."""

    latitude: float
    longitude: float


@dataclass(frozen=True, slots=True)
class TransverseMercatorProjection:
    """Convert DCS theater coordinates to and from WGS84."""

    central_meridian: int
    false_easting: float
    false_northing: float
    scale_factor: float
    _point_to_lat_lon: Transformer
    _lat_lon_to_point: Transformer

    def __init__(
        self,
        *,
        central_meridian: int,
        false_easting: float,
        false_northing: float,
        scale_factor: float,
    ) -> None:
        object.__setattr__(self, "central_meridian", central_meridian)
        object.__setattr__(self, "false_easting", false_easting)
        object.__setattr__(self, "false_northing", false_northing)
        object.__setattr__(self, "scale_factor", scale_factor)

        crs = self.to_crs()
        object.__setattr__(
            self,
            "_point_to_lat_lon",
            Transformer.from_crs(crs, CRS("WGS84")),
        )
        object.__setattr__(
            self,
            "_lat_lon_to_point",
            Transformer.from_crs(CRS("WGS84"), crs),
        )

    def to_crs(self) -> CRS:
        """Return the projected CRS used by the DCS theater."""

        return CRS.from_proj4(
            " ".join(
                [
                    "+proj=tmerc",
                    "+lat_0=0",
                    f"+lon_0={self.central_meridian}",
                    f"+k_0={self.scale_factor}",
                    f"+x_0={self.false_easting}",
                    f"+y_0={self.false_northing}",
                    "+towgs84=0,0,0,0,0,0,0",
                    "+units=m",
                    "+vunits=m",
                    "+ellps=WGS84",
                    "+no_defs",
                    "+axis=neu",
                ]
            )
        )

    def to_lat_lon(self, point: DcsPoint) -> LatLon:
        """Project a DCS meter coordinate into WGS84 decimal degrees."""

        latitude, longitude = self._point_to_lat_lon.transform(point.x, point.y)
        return LatLon(latitude=latitude, longitude=longitude)

    def to_dcs_point(self, lat_lon: LatLon) -> DcsPoint:
        """Project a WGS84 decimal degree coordinate into DCS meters."""

        x, y = self._lat_lon_to_point.transform(
            lat_lon.latitude,
            lat_lon.longitude,
        )
        return DcsPoint(x=x, y=y)
