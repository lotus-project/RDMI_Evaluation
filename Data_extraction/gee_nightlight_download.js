var geometry1 = 
    /* color: #00ffff */
    /* displayProperties: [
      {
        "type": "rectangle"
      }
    ] */
    ee.Geometry.Polygon(
        [[[-174.07610191601634, 83.91659844617513],
          [-174.07610191601634, 33.52218773560799],
          [5.572335583983659, 33.52218773560799],
          [5.572335583983659, 83.91659844617513]]], null, false),
    geometry2 = 
    /* color: #00ff00 */
    /* displayProperties: [
      {
        "type": "rectangle"
      }
    ] */
    ee.Geometry.Polygon(
        [[[-173.78665416297986, 33.2283454840295],
          [-173.78665416297986, -57.5519473723088],
          [5.686002087020142, -57.5519473723088],
          [5.686002087020142, 33.2283454840295]]], null, false),
    geometry3 = 
    /* color: #0000ff */
    /* displayProperties: [
      {
        "type": "rectangle"
      }
    ] */
    ee.Geometry.Polygon(
        [[[5.629437135506578, 83.80423285990408],
          [5.629437135506578, 33.818127768700535],
          [185.27787463550635, 33.818127768700535],
          [185.27787463550635, 83.80423285990408]]], null, false),
    geometry4 = 
    /* color: #999900 */
    /* displayProperties: [
      {
        "type": "rectangle"
      }
    ] */
    ee.Geometry.Polygon(
        [[[5.980999635506539, 33.598786715355025],
          [5.980999635506539, -56.88338310705519],
          [185.62943713550635, -56.88338310705519],
          [185.62943713550635, 33.598786715355025]]], null, false);


var dataset = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG').filter(ee.Filter.date('2018-03-01', '2019-03-31'));

var nightTime = dataset.select('avg_rad');

var nightTimeVis = {min: 0, max: 100};

Map.addLayer(nighttime, nighttimeVis, 'Nighttime');


// Export to Google Drive
// Run this script for each geometry
Export.image.toDrive({
  image: nightTime,
  description: 'NightLight_1',
  region: geometry1,
  scale: 1000,
  maxPixels: 900000000
})

// region needs to be changed to the corresponding geometry
// scale is equal to the spatial resolution in metres per pixel
// maxPixels has been adjusted to change the maximum amount of pixels in the image as the default is too small for the geometry and scale being used