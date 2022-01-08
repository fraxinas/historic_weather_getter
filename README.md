# historic_weather_getter

(CC) 2022 by Andreas Frisch <github@fraxinas.dev>

## OwO what's this?
**`historic_weather_getter` Imports weather data from www.timeanddate.com**

## Usage
`./historic_weather_getter.py YEAR LOCATION`

where LOCATION has the format country/city

* The script will proceed to asynchronously download and parse all days of the given year
* Sample resolution is usually 30 minutes
* Available values: temperature (°C), humidity (%), wind speed (km/h), pressure (mbar) & condition (text)
* Progress / Error messages are printed to STDERR
* The final result is converted to JSON and pretty printed to STDOUT
* so the parsed result can be redirected into a file e.g.

`./historic_weather_getter.py 2021 germany/frankfurt > frankfurt_weather_2021.txt`

## Disclaimer
The weather data is copyrighted by customweather.com and you're probably not supposed to use it for anything.
