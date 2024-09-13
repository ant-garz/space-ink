# Space ink
Show the [NASA Astronomy Picture of the Day](https://apod.nasa.gov/apod/astropix.html) on an e-ink paper display
![Photo of e paper module displaying a photo from NASA's astronomy picture of the day.](assets/photo.jpg)

## Hardware used
- [5.65inch e-Paper Module (F)](https://www.waveshare.com/wiki/5.65inch_e-Paper_Module_(F)_Manual#Overview)
- [Raspberry Pi Zero 2](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)

## Helpful links
- [Guide on working with the epaper module and a raspberry pi](https://www.waveshare.com/wiki/5.65inch_e-Paper_Module_(F)_Manual#Working_With_Raspberry_Pi)

- The waveshare website and resource guide was helpful for
   - connecting the module to the raspberry pi
   - walkthrough on enabling SPI interface
   - walkthrough on python dependencies necessary for the module to work

## Extra steps to work with vendor code
- download waveshare git repository at [https://github.com/waveshareteam/e-Paper](https://github.com/waveshareteam/e-Paper)
- copy paste `lib` directory from `RaspberryPi_JetsonNano/python/lib` in the repository into the root directory of the space-ink project/repository
- in root directory of space-ink, make your own `fonts` folder
- find `Font.ttc` file from the waveshare git repository located in the `RaspberryPi_JetsonNano/python/pic` folder and paste it into your newly created `fonts` folder in space-ink

## Scheduling with cron
For this project to update on it's own with each new day, I used the `cron` service to schedule the script to be run daily.

- Open the crontab file with the command `crontab -e`
- Add a new line with the schedule to run the script daily
   - I chose to run this script everday at 8am. You can update this as desired. A helpful website I have used in the past is [https://crontab.guru/](https://crontab.guru/)
   - `0 8 * * * sudo /usr/bin/python /home/USER/space-ink/space-ink.py`
- Add a new line with the schedule to run the script when the system reboots
    - `@reboot  sleep 200 && sudo /usr/bin/python /home/USER/space-ink/space-ink.py`
- Save and exit the file

## (optional) Write output of the script to logfile
When I was updating the project and developing I found myself running into issues and bugs to where I could not determine if the script was running or where it was erroring out. To see the output of the script being ran I modified the crontab schedule above with the following commands to see the output of the python script be written to a logfile for my troubleshooting. 
- `0 8 * * * sudo /usr/bin/python /home/USER/space-ink/space-ink.py >> /home/USER/scripts/script.log`
- `@reboot  sleep 200 && sudo /usr/bin/python /home/USER/space-ink/space-ink.py >> /home/USER/scripts/script.log`

With this update, the output for the scheduled jobs is written to `script.log` and we can see what happens when the script is called by the schedule.