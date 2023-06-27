.. _data_overview:

=============
Data overview
=============

There are four key types of input data required: exposure data (vector and raster), vulnerability data (damage functions), hazard maps, and a settings file. It is recommended to organize the files in the following folder structure.

.. |folder_icon| image:: ../../_static/icons8-folder.svg
   :height: 25ex

.. |file_icon| image:: ../../_static/icons8-file.svg
   :height: 25ex

* |folder_icon| exposure

* |folder_icon| hazard

* |folder_icon| vulnerability

* |file_icon| settings.toml


Settings
========

The settings file (\*.toml) contains information about the data that should be used for the risk assessment. Delft-FIAT can be run (REFER TO RUN SECTION OF THE DOCUMENTATION) by simply pointing to a settings.toml file. A filled-in example with explanation about the parameters is given below::

  [global]
  output_dir = 'output' # Directory to save the results in. The directory is relative to the settings.toml file or absolute.
  crs = 'EPSG:32617' # CRS of your output file (gpkg).

  [hazard]
  grid_file = 'hazard\event_map.nc' # Path to netCDF file, relative to the setting.toml file or absolute. It can contain one (for events) or multiple (for return periods) bands.
  crs = 'EPSG:32617' # Only compulsory if the CRS is unknown in the grid_file.
  risk = True # True or False, if True, risk (EAD) is calculated.
  spatial_reference = 'DEM' # DEM or Datum for respectively a water depth or water elevation map.

  [exposure.vector]
  dbase_file = 'exposure\exposure.csv' # Contains vector assets and can be linked to multiple geometries in geopackages.
  crs = 'EPSG:32617' # Only compulsory if the CRS is unknown in the geopackages.
  file = ['exposure\polygons.gpkg', 'exposure\points.gpkg'] # Geopackages to link to the assets in the dbase_file. Links from the Object_ID attribute to the Object ID attribute in the dbase_file.

  [exposure.grid]
  crs = 'EPSG:32617' # Only compulsory if the CRS is unknown in the NetCDF file of the exposure grid(s).
  file = 'exposure\raster.nc' # Contains raster exposure data.

  [vulnerability]
  dbase_file = 'vulnerability\vulnerability_curves.csv' # Contains the required vulnerability curves.


Exposure - vector
=================

Delft-FIAT requires one exposure database CSV file and one or multiple point or polygon GeoPackages. The exposure CSV file contains information about each asset in the area of interest that is needed for the damage calculation. Each row represents an asset, such as a building, road segment, or utility, and each column represents an attribute of the object, such as its location, elevation or maximum potential damage value.



Exposure - raster
=================

Coming later...

Vulnerability
=============

Coming later...

Hazard
======

Coming later...
