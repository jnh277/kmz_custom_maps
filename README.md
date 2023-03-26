# kmz custom maps


A simple python script for processing a kmz image overlap so that it 
conforms to the requirements to be used as a Garmin custom map.


Garmin provides instructions for creating a custom map here

https://support.garmin.com/en-US/?faq=cVuMqGHWaM7wTFWMkPNLN9

However, the catch is that the kmz files must conform to the requirements
listed here

https://support.garmin.com/en-AU/?faq=UcO3cFueS12IwCnizrJjeA

The most restrictive part is that the jpegs included in the 
kmz cannot have more than 1024 by 1024 pixels.

This python script solve this problem by taking a kmz file with 
a single larger jpeg and turning it into a kmz file with a 
number of smaller tiled jpegs.

I have done minimal testing of this, other than checking that it does
work on my Garmin GPSMAP 66i. So use at own risk.

Requirements
- Python >= 3.9

Usage:
```
pip install kmz_custom_maps
```

```
python -m kmz_custom_map.run ./path/to/map.kmz
```

The processed kmz will be added to the directory the script was run from.

For a 1:25k topo map converted to a jpeg using 200 pixels per inch. 
this creates a kmz with about 40 jpeg images. I would be mindful to not
have too many of these custom maps on a garmin device at any time as it 
does seem to slow down rendering.

Optionally, if you want to create many separate kmz files corresponding
to tiles from the original kmz you can run it this way
```
python -m kmz_custom_map.run --combine ./path/to/map.kmz
```
 
