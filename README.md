# Python library for the Withings devices


While withings provide a nifty API to fetch body metrics,
<http://oauth.withings.com/api/doc>

there is actually no way to retrive other information about a dedicated device (in this case the scale W-50).

So here is a simple class using the web dashboard api (undocumented). Works for my personnal usage.

Installation:

    pip install git+https://github.com/CyrilPeponnet/withings-devices.git

Usage:

``` python
from withings-devices import WithingsDevices

my_devices = WithingsDevices('YOUR_EMAIL', 'YOUR_PASSWORD')

# fetch the devices
my_devices.fetch_devices()

print my_devices.devices
{12342: {'batt_lvl': 42, 'name': u'My Scale', 'lastseen': 1421528371}}

#with 12342 as the deviceid

# fetch the data last recorded data
my_devices.fetch_data()

print my_devices.devices
{12342: {'batt_lvl': 42, 'name': u'My Scale', 'data': {'co2': [{u'date': 1421528371, u'value': 1155}], 'temperature': [{u'date': 1421528371, u'value': 19.6}]}, 'lastseen': 1421528371}}

# fetch a speficic device and ask for a full period of data
my_devices.fetch_data(deviceid=12342,last_days=200)

...

```

Enjoy