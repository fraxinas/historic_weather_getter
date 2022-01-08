#! /usr/bin/python3
# -*- coding: utf-8 -*-

'''
  historic_weather_getter.py
  Copyright (C) 2022 Andreas Frisch <github@fraxinas.dev>

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or (at
  your option) any later version.

  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
  USA.
'''
import sys
import asyncio
import aiohttp
import json
import re
from calendar import monthrange

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class DateDownloader:
    def __init__(self):
        try:
            year = int(sys.argv[1])
            location = sys.argv[2]
        except:
            print(f"Usage:\t{sys.argv[0]} YEAR LOCATION\n\tLOCATION has the format country/city")
            cfg_file = sys.path[0] + '/config.json'
            sys.exit(1)

        self.base_uri = f"https://www.timeanddate.com/scripts/cityajax.php?n={location}&mode=historic&json=1"
        self.weather_table = {}
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.gatherDates(year))
        eprint("finished.")
        print(json.dumps(self.weather_table, indent=4, sort_keys=True))

    async def gatherDates(self, year):
        for month in range(12):
            month = month+1
            tasks = set()
            num_days = monthrange(year, month)[1]
            for day in range(num_days):
                day = day+1
                task = asyncio.create_task(self.getDate(year,month,day))
                tasks.add(task)
                await asyncio.gather(*tasks)

    async def getDate(self, year, month, day):
        uri = f"{self.base_uri}&hd={year}{month:02d}{day:02d}&month={month:02d}&year={year}"
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as resp:
                if resp.status == 200:
                    eprint(f"Successfully received data for {year}-{month:02d}-{day:02d}.")
                    await self.convertData(await resp.read(), year, month, day)
                else:
                    eprint(f"Error code={resp.status}")

    async def convertData(self, rawdata, year, month, day):
        data = rawdata.decode("utf-8")
        data = data.replace('c:','"c":').replace('h:','"h":').replace('s:','"s":')
        try:
            structured_data = json.loads(data)
        except json.decoder.JSONDecodeError as e:
            eprint(f"JSONDecodeError {e} when decoding {data}")
            return
        re_int = re.compile("(-?\d+)")
        temp = windspeed = humidity = 0
        for sample in structured_data:
            sample_list = sample["c"]
            (rawtime, _, rawtemp, rawcond, rawwindspeed, rawwinddir, rawhum, rawpress, _) = (x["h"] for x in sample_list)
            time = rawtime[:5]
            try:
                temp = re_int.match(rawtemp).group(1)
            except AttributeError:
                eprint(f"Error parsing temperature field '{rawtemp}'!")
            if rawwindspeed in ("No wind", "N/A"):
                windspeed = 0
            else:
                try:
                    windspeed = re_int.match(rawwindspeed).group(1)
                except AttributeError:
                    eprint(f"Error parsing windspeed field '{rawwindspeed}'!")
            try:
                humidity = re_int.match(rawhum).group(1)
            except AttributeError:
                eprint(f"Error parsing humidity field '{rawhum}'!")
            pressure = re_int.match(rawpress).group(1)
            eprint(f"{year}-{month:02d}-{day:02d} {time}: {temp} °C, {windspeed} km/h, {humidity} %, {pressure} mbar, {rawcond}")
            date_time = f"{year}-{month:02d}-{day:02d} {time}"
            self.weather_table[date_time] = [temp, humidity, windspeed, pressure, rawcond]

if __name__ == "__main__":
    downloader = DateDownloader()
