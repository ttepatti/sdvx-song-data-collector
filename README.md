# sdvx-song-data-collector

This is a Python3 script that uses RemyWiki's MediaWiki API to gather data about SDVX songs.

The main purpose of this data collection was to create a CSV file of every single SDVX song, which could then have other analysis performed on it. Which years had the most songs added to the game? What month is most common for updates? What day of the week? What's the average BPM of songs added to the game, year-to-year? Lots of fun data analysis!

## Disclaimer

Please be careful when using this script - don't let it collect data too fast or you could overwhelm RemyWiki with your requests. Its default speed is to send requests extremely slowly, at only one request per second.
