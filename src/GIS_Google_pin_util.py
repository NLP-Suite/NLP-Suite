import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_packages(GUI_util.window, "GIS_Google_pin_util",
										  ['os', 'simplekml', 'tkinter']) == False:
	sys.exit(0)

import os
import simplekml
import tkinter.messagebox as mb
import pandas as pd

import IO_csv_util
import IO_user_interface_util

# icon_type are the different types of icon, like pushpin, paddle teardrop, paddle square....
# 	Expected input will be a string, for example: icon_type == "pushpin"
# icon_style are the different styles of a specific icon, like pushpin has different colors, paddle teardrop has more styles including numbers, letters, colors and more
#	Expected input will be a string, for example: icon_style == "blue"
# View all icon types and styles here:
#		http://kml4earth.appspot.com/icons.html#pushpin

# called from GIS_GUI
# must be connected to the internet
def pin_icon_select(icon_type, icon_style):
	icon_url = "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"
	if icon_type == "Directions":
		# direction style, 17 styles in total
		if icon_style == "none":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-none.png'
		elif icon_style == "North (track 0)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-0.png'
		elif icon_style == "Northeast (track 1)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-1.png'
		elif icon_style == "Northeast (track 2)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-2.png'
		elif icon_style == "Northeast (track 3)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-3.png'
		elif icon_style == "East (track 4)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-4.png'
		elif icon_style == "Southeast (track 5)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-5.png'
		elif icon_style == "Southeast (track 6)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-6.png'
		elif icon_style == "Southeast (track 7)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-7.png'
		elif icon_style == "South (track 8)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-8.png'
		elif icon_style == "Southwest (track 9)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-9.png'
		elif icon_style == "Southwest (track 10)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-10.png'
		elif icon_style == "Southwest (track 11)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-11.png'
		elif icon_style == "West (track 12)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-12.png'
		elif icon_style == "Northwest (track 13)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-13.png'
		elif icon_style == "Northwest (track 14)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-14.png'
		elif icon_style == "Northwest (track 15)":
			icon_url = 'http://earth.google.com/images/kml-icons/track-directional/track-15.png'

	# Paddle teardrop styles
	elif icon_type == "Paddles (teardrop)":
		# Number style, from 1 to 10
		if icon_style == "1":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/1.png'
		elif icon_style == "2":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/2.png'
		elif icon_style == "3":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/3.png'
		elif icon_style == "4":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/4.png'
		elif icon_style == "5":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/5.png'
		elif icon_style == "6":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/6.png'
		elif icon_style == "7":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/7.png'
		elif icon_style == "8":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/8.png'
		elif icon_style == "9":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/9.png'
		elif icon_style == "10":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/10.png'

		# Letter style, from A to Z
		elif icon_style == "A":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/A.png'
		elif icon_style == "B":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/B.png'
		elif icon_style == "C":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/C.png'
		elif icon_style == "D":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/D.png'
		elif icon_style == "E":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/E.png'
		elif icon_style == "F":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/F.png'
		elif icon_style == "G":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/G.png'
		elif icon_style == "H":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/H.png'
		elif icon_style == "I":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/I.png'
		elif icon_style == "J":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/J.png'
		elif icon_style == "K":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/K.png'
		elif icon_style == "L":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/L.png'
		elif icon_style == "M":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/M.png'
		elif icon_style == "N":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/N.png'
		elif icon_style == "O":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/O.png'
		elif icon_style == "P":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/P.png'
		elif icon_style == "Q":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/Q.png'
		elif icon_style == "R":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/R.png'
		elif icon_style == "S":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/S.png'
		elif icon_style == "T":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/T.png'
		elif icon_style == "U":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/U.png'
		elif icon_style == "V":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/V.png'
		elif icon_style == "W":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/W.png'
		elif icon_style == "X":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/X.png'
		elif icon_style == "Y":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/Y.png'
		elif icon_style == "Z":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/Z.png'

		# Go/Pause/Stop style, 3 styles in total (go is green, pause is yellow, stop is red)
		elif icon_style == "go-sign(green)":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/go.png'
		elif icon_style == "pause-sign(yellow)":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/pause.png'
		elif icon_style == "stop-sign(red)":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/stop.png'

		# Color and pattern style, 9 styles in total (blue, green, light blue, pink, purple, red, white, yellow, orange)
		elif icon_style == "blue-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-blank.png'
		elif icon_style == "blue-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-circle.png'
		elif icon_style == "blue-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-diamond.png'
		elif icon_style == "blue-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-square.png'
		elif icon_style == "blue-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-stars.png'

		elif icon_style == "green-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-blank.png'
		elif icon_style == "green-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png'
		elif icon_style == "green-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-diamond.png'
		elif icon_style == "green-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-square.png'
		elif icon_style == "green-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-stars.png'

		elif icon_style == "light-blue-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ltblu-blank.png'
		elif icon_style == "light-blue-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png'
		elif icon_style == "light-blue-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ltblu-diamond.png'
		elif icon_style == "light-blue-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ltblu-square.png'
		elif icon_style == "light-blue-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ltblu-stars.png'

		elif icon_style == "pink-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/pink-blank.png'
		elif icon_style == "pink-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/pink-circle.png'
		elif icon_style == "pink-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/pink-diamond.png'
		elif icon_style == "pink-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/pink-square.png'
		elif icon_style == "pink-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/pink-stars.png'

		elif icon_style == "purple-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-blank.png'
		elif icon_style == "purple-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-circle.png'
		elif icon_style == "purple-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-diamond.png'
		elif icon_style == "purple-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-square.png'
		elif icon_style == "purple-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-stars.png'

		elif icon_style == "red-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
		elif icon_style == "red-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/red-diamond.png'
		elif icon_style == "red-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/red-square.png'
		elif icon_style == "red-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'

		elif icon_style == "white-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
		elif icon_style == "white-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
		elif icon_style == "white-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-diamond.png'
		elif icon_style == "white-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-square.png'
		elif icon_style == "white-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-stars.png'

		elif icon_style == "yellow-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png'
		elif icon_style == "yellow-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png'
		elif icon_style == "yellow-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-diamond.png'
		elif icon_style == "yellow-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-square.png'
		elif icon_style == "yellow-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png'

		elif icon_style == "orange-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/orange-blank.png'
		elif icon_style == "orange-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/orange-circle.png'
		elif icon_style == "orange-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/orange-diamond.png'
		elif icon_style == "orange-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/orange-square.png'
		elif icon_style == "orange-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/orange-stars.png'

	# Paddle square styles
	elif icon_type == "Paddles (square)":
		# Number style, from 1 to 10
		if icon_style == "1":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/1-lv.png'
		elif icon_style == "2":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/2-lv.png'
		elif icon_style == "3":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/3-lv.png'
		elif icon_style == "4":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/4-lv.png'
		elif icon_style == "5":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/5-lv.png'
		elif icon_style == "6":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/6-lv.png'
		elif icon_style == "7":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/7-lv.png'
		elif icon_style == "8":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/8-lv.png'
		elif icon_style == "9":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/9-lv.png'
		elif icon_style == "10":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/10-lv.png'

		# Go/Pause/Stop style, 3 styles in total (go is green, pause is yellow, stop is red)
		elif icon_style == "go-sign(green)":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/go-lv.png'
		elif icon_style == "pause-sign(yellow)":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/pause-lv.png'
		elif icon_style == "stop-sign(red)":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/stop-lv.png'

		# Color and pattern style, 6 styles in total (blue, green, purple, red, white, yellow)
		elif icon_style == "blue-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-blank-lv.png'
		elif icon_style == "blue-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-circle-lv.png'
		elif icon_style == "blue-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-diamond-lv.png'
		elif icon_style == "blue-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-square-lv.png'
		elif icon_style == "blue-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/blu-stars-lv.png'

		elif icon_style == "green-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-blank-lv.png'
		elif icon_style == "green-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-circle-lv.png'
		elif icon_style == "green-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-diamond-lv.png'
		elif icon_style == "green-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-square-lv.png'
		elif icon_style == "green-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/grn-stars-lv.png'

		elif icon_style == "purple-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-blankv.png'
		elif icon_style == "purple-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-circle-lv.png'
		elif icon_style == "purple-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-diamond-lv.png'
		elif icon_style == "purple-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-square-lv.png'
		elif icon_style == "purple-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/purple-stars-lv.png'

		elif icon_style == "red-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/red-circle-lv.png'
		elif icon_style == "red-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/red-diamond-lv.png'
		elif icon_style == "red-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/red-square-lv.png'
		elif icon_style == "red-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/red-stars-lv.png'

		elif icon_style == "white-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank-lv.png'
		elif icon_style == "white-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-circle-lv.png'
		elif icon_style == "white-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-diamond-lv.png'
		elif icon_style == "white-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-square-lv.png'
		elif icon_style == "white-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/wht-stars-lv.png'

		elif icon_style == "yellow-blank":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-blank-lv.png'
		elif icon_style == "yellow-circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-circle-lv.png'
		elif icon_style == "yellow-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-diamond-lv.png'
		elif icon_style == "yellow-square":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-square-lv.png'
		elif icon_style == "yellow-stars":
			icon_url = 'http://maps.google.com/mapfiles/kml/paddle/ylw-stars-lv.png'

	# Pushpin styles
	elif icon_type == "Pushpins":
		# All colors, 8 in total (blue, green, light blue, pink, purple, red, white, yellow)
		if icon_style == "blue":
			icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png'
		elif icon_style == "green":
			icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/grn-pushpin.png'
		elif icon_style == "light_blue":
			icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/ltblu-pushpin.png'
		elif icon_style == "pink":
			icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/pink-pushpin.png'
		elif icon_style == "purple":
			icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/purple-pushpin.png'
		elif icon_style == "red":
			icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png'
		elif icon_style == "white":
			icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'
		elif icon_style == "yellow":
			icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'

	# Shapes style
	elif icon_type == "Shapes":
		# 103 shapes in total, first 98 are in aplphabetic order of thier first letter
		# last 5 are differnet weathers
		if icon_style == "airports":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/airports.png'
		elif icon_style == "arrow-reverse":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/arrow-reverse.png'
		elif icon_style == "arrow":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/arrow.png'
		elif icon_style == "arts":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/arts.png'
		elif icon_style == "bars":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/bars.png'
		elif icon_style == "broken_link":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/broken_link.png'
		elif icon_style == "bus":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/bus.png'
		elif icon_style == "cabs":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/arts.png'
		elif icon_style == "camera":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/camera.png'
		elif icon_style == "campfire":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/campfire.png'
		elif icon_style == "campground":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/campground.png'
		elif icon_style == "capital_big":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/capital_big.png'
		elif icon_style == "capital_big_highlight":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/capital_big_highlight.png'
		elif icon_style == "capital_small":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/capital_small.png'
		elif icon_style == "capital_small_highlight":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/capital_small_highlight.png'
		elif icon_style == "caution":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/caution.png'
		elif icon_style == "church":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/church.png'
		elif icon_style == "coffee":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/coffee.png'
		elif icon_style == "convenience":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/convenience.png'
		elif icon_style == "cross-hairs":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png'
		elif icon_style == "cross-hairs_highlight":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/cross-hairs_highlight.png'
		elif icon_style == "cycling":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/cycling.png'
		elif icon_style == "dining":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/dining.png'
		elif icon_style == "dollar":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/dollar.png'
		elif icon_style == "donut":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/donut.png'
		elif icon_style == "earthquake":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/earthquake.png'
		elif icon_style == "electronics":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/electronics.png'
		elif icon_style == "euro":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/euro.png'
		elif icon_style == "falling_rocks":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/falling_rocks.png'
		elif icon_style == "ferry":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/ferry.png'
		elif icon_style == "firedept":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/firedept.png'
		elif icon_style == "fishing":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/fishing.png'
		elif icon_style == "flag":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/flag.png'
		elif icon_style == "forbidden":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/forbidden.png'
		elif icon_style == "gas_stations":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/gas_stations.png'
		elif icon_style == "golf":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/golf.png'
		elif icon_style == "grocery":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/grocery.png'
		elif icon_style == "heliport":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/heliport.png'
		elif icon_style == "highway":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/highway.png'
		elif icon_style == "hiker":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/hiker.png'
		elif icon_style == "homegardenbusiness":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/homegardenbusiness.png'
		elif icon_style == "horsebackriding":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/horsebackriding.png'
		elif icon_style == "hospitals":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/hospitals.png'
		elif icon_style == "info-i":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/info-i.png'
		elif icon_style == "info":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/info.png'
		elif icon_style == "info_circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/info_circle.png'
		elif icon_style == "lodging":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/lodging.png'
		elif icon_style == "man":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/man.png'
		elif icon_style == "marina":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/marina.png'
		elif icon_style == "mechanic":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/mechanic.png'
		elif icon_style == "motorcycling":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/motorcycling.png'
		elif icon_style == "mountains":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/mountains.png'
		elif icon_style == "movies":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/movies.png'
		elif icon_style == "open-diamond":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/open-diamond.png'
		elif icon_style == "parking_lot":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/parking_lot.png'
		elif icon_style == "parks":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/parks.png'
		elif icon_style == "pharmacy_rx":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/pharmacy_rx.png'
		elif icon_style == "phone":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/phone.png'
		elif icon_style == "picnic":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/picnic.png'
		elif icon_style == "placemark_circle":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
		elif icon_style == "placemark_circle_highlight":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png'
		elif icon_style == "placemark_square":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/placemark_square.png'
		elif icon_style == "placemark_square_highlight":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/placemark_square_highlight.png'
		elif icon_style == "play":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/play.png'
		elif icon_style == "poi":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/poi.png'
		elif icon_style == "police":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/police.png'
		elif icon_style == "polygon":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/polygon.png'
		elif icon_style == "post_office":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/post_office.png'
		elif icon_style == "rail":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/rail.png'
		elif icon_style == "ranger_station":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/ranger_station.png'
		elif icon_style == "realestate":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/realestate.png'
		elif icon_style == "road_shield1":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/road_shield1.png'
		elif icon_style == "road_shield2":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/road_shield2.png'
		elif icon_style == "road_shield3":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/road_shield3.png'
		elif icon_style == "ruler":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/ruler.png'
		elif icon_style == "sailing":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/sailing.png'
		elif icon_style == "salon":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/salon.png'
		elif icon_style == "schools":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/schools.png'
		elif icon_style == "shaded_dot":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png'
		elif icon_style == "shopping":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/shopping.png'
		elif icon_style == "ski":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/ski.png'
		elif icon_style == "snack_bar":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/snack_bar.png'
		elif icon_style == "square":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/square.png'
		elif icon_style == "star":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/star.png'
		elif icon_style == "subway":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/subway.png'
		elif icon_style == "swimming":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/swimming.png'
		elif icon_style == "target":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/target.png'
		elif icon_style == "terrain":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/terrain.png'
		elif icon_style == "toilets":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/toilets.png'
		elif icon_style == "trail":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/trail.png'
		elif icon_style == "tram":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/tram.png'
		elif icon_style == "triangle":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/triangle.png'
		elif icon_style == "truck":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/truck.png'
		elif icon_style == "volcano":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/volcano.png'
		elif icon_style == "water":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/water.png'
		elif icon_style == "webcam":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/webcam.png'
		elif icon_style == "wheel_chair_accessible":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/wheel_chair_accessible.png'
		elif icon_style == "woman":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/woman.png'
		elif icon_style == "yen":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/yen.png'
		elif icon_style == "sunny":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/sunny.png'
		elif icon_style == "partly_cloudy":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/partly_cloudy.png'
		elif icon_style == "snowflake_simple":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/snowflake_simple.png'
		elif icon_style == "rainy":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/rainy.png'
		elif icon_style == "thunderstorm":
			icon_url = 'http://maps.google.com/mapfiles/kml/shapes/thunderstorm.png'

	return icon_url


# inputFilename is a csv file generated by the NER_extractor
# customize pins for Google Earth Pro
# called from GIS_KML_util
def pin_customizer(inputFilename, pnt, geo_index, index_list, locationColumnName,sentence='',
				   group_var=0, group_number_var=1, group_values=[''], group_labels=[''],
				   icon_type_list=['Pushpins'], icon_style_list=['red'],
				   icon_url='http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png',
				   name_var_list=[0], scale_var_list=['1'],
				   color_var_list=[0], color_style_var_list=[''],
				   bold_var_list=[1], italic_var_list=[1],
				   description_var_list=[1], description_csv_field_var_list=['Sentence'],
				   j=0, data=None, headers=None):
	if data is None:
		withHeader_var = IO_csv_util.csvFile_has_header(inputFilename)  # check if the file has header
		data, headers = IO_csv_util.get_csv_data(inputFilename, withHeader_var)  # get the data and header

	# startTime = IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'GIS kml pin customizer', 'Started running kml pin customizer at',
	# 											   True, '', True, '', silent=True)

	# Assign description
	if description_var_list[j] == 1:
		if len(description_csv_field_var_list[j]) == 0:
			mb.showwarning(title='No CSV Field Selected for Description for Group No.' + str(j + 1),
						   message='The description checkbox is ticked but no csv field was selected for the Group No.' + str(
							   j + 1) + '.\n\nPlease, check your input and try again.')
			sys.exit()
		if group_var == 1:
			if len(group_labels[j]) < 1:
				mb.showwarning(title='No Group Labels Specified for Group No.' + str(j + 1),
							   message='There is no group label specified for Group No.' + str(
								   j + 1) + '.\n\nThe program will automatically set a group label for this group as "Group ' + str(
								   j + 1) + '".')
				new_label = "Group " + str(j + 1)
				group_labels[j] = new_label

		pnt = pin_description(inputFilename, pnt, data, headers, geo_index, index_list,
						locationColumnName, sentence,
						group_var, group_values, group_labels, j,
						name_var_list[j], description_csv_field_var_list[j],
						italic_var_list[j], bold_var_list[j])
	# Assign name
	if name_var_list[j] == 1:
		pnt = pin_name(pnt, data, headers, geo_index, description_csv_field_var_list[j], scale_var_list[j],
					   color_var_list[j], color_style_var_list[j])

	# IO_user_interface_util.timed_alert(GUI_util.window, 3000, 'GIS kml pin customizer', 'Finished running kml pin customizer at', True, '',
	# 								   True, startTime, silent=True)

	return pnt


# Add description to each point
# data is all the data from the inputfile, a double list [[]]
# 	Expected format: [[Atlanta, A, A, Georgia, ...], [Boston, B, B, Massachuttes, ...], [Charlotte, C, C, Notrh Carolina, ....]]
# headers is the inputfile's headers
#	Expected format: [City, latitude, longitude, State, .....]
# Index is the number of the city we are currently plotting the point
#	For example, from the example above, Atlanta will be 1, Boston will be 2....
# Column_name is the description_var (passed from GUI, the drop down menu, which column we want to put as description)
#	Expected format: column_name ==  "State"
# inputFilename is a csv file generated by the NER_extractor


# icon_url = 'http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png',
# name_var_list = [0], scale_var_list = ['1'],
# color_var_list = [0], color_style_var_list = [''],
#
# description_var_list = [1], description_csv_field_var_list = ['Sentence'],
# j = 0, data = None, headers = None):

def pin_description(inputFilename, pnt, data, headers, geo_index, index_list,
					description_location_var_name='Location',sentence='',
					group_var =0, group_values = [''], group_labels = [''],
					j=0, name_var=0, description_csv_field_var='Sentence',
					italic_var = [1], bold_var = [1]):
	# # TODO if the inputFilename contains more than one document then the document name should be listed in descriptions
	if 'Document ID' in headers:
		nDocs = IO_csv_util.GetMaxValueInCSVField(inputFilename, 'GIS_Google_pin', 'Document ID')

	if description_location_var_name=='NER':
		description_location_var_name='Location'

	if sentence=='':
		# the input filename contains the list of NER non-geocoded LOCATIONS
		# it is used to extract the sentence to be displayed when clicking on the pin
		document_num = 0
		documents = []
		names = []
		description = []
		for a in range(len(headers)):
			if 'Document' == headers[a]:
				document_num = a
			if description_csv_field_var == headers[a]:  # description_csv_field_var is typically set to sentence
				column_num = a
			if description_location_var_name == headers[a]:
				location_num = a
		# TODO MINO Pandas
		data = pd.read_csv(inputFilename)
		names = data['Location'].values.tolist()
		description = data['Sentence'].values.tolist()
		documents = data['Document'].apply(IO_csv_util.undressFilenameForCSVHyperlink)
		documents = documents.apply(os.path.split)
		documents = [item[1] for _,item in documents.items()]

	index = index_list[geo_index - 1]

	if group_var == 1:
		group_value = group_values[j]
		group_label = group_labels[j]
		if name_var == 0:
			if description_location_var_name == description_csv_field_var:
				if italic_var == 1 and bold_var == 1:
					pnt.description = "<i><b>Location</b></i>: " + names[
						index - 1] + "<br/><br/><i><b>Group Label</b></i>: " + group_label + "<br/><br/><i><b>Group Value</b></i>: " + group_value
				elif bold_var == 1:
					pnt.description = "<b>Location</b>: " + names[
						index - 1] + "<br/><br/><b>Group Label</b>: " + group_label + "<br/><br/><b>Group Value</b>: " + group_value
				elif italic_var == 1:
					pnt.description = "<i>Location</i>: " + names[
						index - 1] + "<br/><br/><i>Group Label</i>: " + group_label + "<br/><br/><i>Group Value</i>: " + group_value
				else:
					pnt.description = "Location: " + names[
						index - 1] + "<br/><br/>" + "Group Label: " + group_label + "<br/><br/>" + "Group Value: " + group_value
			else:
				if italic_var == 1 and bold_var == 1:
					pnt.description = "<i><b>Location</b></i>: " + names[
						index - 1] + "<br/><br/><i><b>Group Label</b></i>: " + group_label + "<br/><br/><i><b>Group Value</b></i>: " + group_value + "<br/><br/><i><b>" + \
									  description_csv_field_var + "</b></i>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<i><b>Document' + "</b></i>" + ": " + documents[index - 1]
				elif bold_var == 1:
					pnt.description = "<b>Location</b>: " + names[
						index - 1] + "<br/><br/><b>Group Label</b>: " + group_label + "<br/><br/><b>Group Value</b>: " + group_value + "<br/><br/><b>" + \
									  description_csv_field_var + "</b>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<b>Document' + "</b>" + ": " + documents[index - 1]
				elif italic_var == 1:
					pnt.description = "<i>Location</i>: " + names[
						index - 1] + "<br/><br/><i>Group Label</i>: " + group_label + "<br/><br/><i>Group Value</i>: " + group_value + "<br/><br/><i>" + \
									  description_csv_field_var + "</i>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<i>Document' + "</i>" + ": " + documents[index - 1]
				else:
					pnt.description = "Location: " + names[
						index - 1] + "<br/><br/>" + "Group Label: " + group_label + "<br/><br/>" + "Group Value: " + group_value + "<br/><br/>" + \
									  description_csv_field_var + ": " + description[index - 1] + "<br/><br/>" + \
									  'Document' + ": " + documents[index - 1]
		else:
			if description_location_var_name == description_csv_field_var:
				if italic_var == 1 and bold_var == 1:
					pnt.description = "<i><b>Group Label</b></i>: " + group_label + "<br/><br/><i><b>Group Value</b></i>: " + group_value
				elif bold_var == 1:
					pnt.description = "<b>Group Label</b>: " + group_label + "<br/><br/><b>Group Value</b>: " + group_value
				elif italic_var == 1:
					pnt.description = "<i>Group Label</i>: " + group_label + "<br/><br/><i>Group Value</i>: " + group_value
				else:
					pnt.description = "Group Label: " + group_label + "<br/><br/>" + "Group Value: " + group_value
			else:
				if italic_var == 1 and bold_var == 1:
					pnt.description = "<i><b>Group Label</b></i>: " + group_label + "<br/><br/><i><b>Group Value</b></i>: " + group_value + "<br/><br/><i><b>" + \
									  description_csv_field_var + "</b></i>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<i><b>Document' + "</b></i>" + ": " + documents[index - 1]
				elif bold_var == 1:
					pnt.description = "<b>Group Label</b>: " + group_label + "<br/><br/><b>Group Value</b>: " + group_value + "<br/><br/><b>" + \
									  description_csv_field_var + "</b>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<b>Document' + "</b>" + ": " + documents[index - 1]
				elif italic_var == 1:
					pnt.description = "<i>Group Label</i>: " + group_label + "<br/><br/><i>Group Value</i>: " + group_value + "<br/><br/><i>" + \
									  description_csv_field_var + "</i>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<i>Document' + "</i>" + ": " + documents[index - 1]
				else:
					pnt.description = "Group Label: " + group_label + "<br/><br/>" + "Group Value: " + group_value + "<br/><br/>" + \
									  description_csv_field_var + ": " + description[index - 1] + "<br/><br/>" + \
									  'Document' + ": " + documents[index - 1]

	elif group_var == 0:
		if name_var == 0:
			if description_location_var_name == description_csv_field_var:
				if italic_var == 1 and bold_var == 1:
					pnt.description = "<i><b>Location</b></i>: " + names[index - 1]
				elif bold_var == 1:
					pnt.description = "<b>Location</b>: " + names[index - 1]
				elif italic_var == 1:
					pnt.description = "<i>Location</i>: " + names[index - 1]
				else:
					pnt.description = "Location: " + names[index - 1]
			else:
				if italic_var == 1 and bold_var == 1:
					pnt.description = "<i><b>Location</b></i>: " + names[index - 1] + "<br/><br/><i><b>" + \
									  description_csv_field_var + "</b></i>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<i><b>Document' + "</b></i>" + ": " + documents[index - 1]
				elif bold_var == 1:
					pnt.description = "<b>Location</b>: " + names[index - 1] + "<br/><br/><b>" + \
									  description_csv_field_var + "</b>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<b>Document' + "</b>" + ": " + documents[index - 1]

				elif italic_var == 1:
					pnt.description = "<i>Location</i>: " + names[index - 1] + "<br/><br/><i>" + \
									  description_csv_field_var + "</i>" + ": " + description[
										  index - 1] + "<br/><br/>" + \
									  '<i>Document' + "</i>" + ": " + documents[index - 1]
				else:
					pnt.description = "Location: " + names[index - 1] + "<br/><br/>" + \
									  description_csv_field_var + ": " + description[index - 1] + "<br/><br/>" + \
									  'Document' + ": " + documents[index - 1]
		else:
			if italic_var == 1 and bold_var == 1:
				pnt.description = "<i><b>" + \
								  description_csv_field_var + "</b></i>" + ": " + description[index - 1] + \
								  '<i><b>Document' + "</b></i>" + ": " + documents[index - 1]

			elif bold_var == 1:
				pnt.description = "<b>" + \
								  description_csv_field_var + "</b>" + ": " + description[index - 1] + \
								  '<b>Document' + "</b>" + ": " + documents[index - 1]

			elif italic_var == 1:
				pnt.description = "<i>" + \
								  description_csv_field_var + "</i>" + ": " + description[index - 1] + \
								  '<i>Document' + "</i>" + ": " + documents[index - 1]

			else:
				pnt.description = description_csv_field_var + ": " + description[index - 1] + \
								  'Document' + ": " + documents[index - 1]

	return pnt


# Add description to each point
# data is all the data from the inputfile
# 	Expected format: [[Atlanta, A, A, Georgia, ...], [Boston, B, B, Massachuttes, ...], [Charlotte, C, C, Notrh Carolina, ....]]
# headers is the inputfile's headers
#	Expected format: [City, latitute, longitude, State, .....]
# Index is the number of the city we are currently plotting the point
#	For example, from the example above, Atlanta will be 1, Boston will be 2....
# description_location_var_name is got from GUI_util, as the column where the locations' names at
#	Expected format: location_var == "Name"
# scale_var is the variable for the scale of the name label
#	Expected format: scale_var == 2 (it is an integer)
# color_var is the variable indicating whether the user choose a color of the name, 1 for yes, 0 for no
#	Expected format: scale_var == 1 (it is an integer) and it will read set color_style_var
#	Expected format: scale_var == 0 (it is an integer) and it will read default color white for color_style_var = (255, 255, 255)
# color_style_var is a string of rgb color code for the name
#	Expected format: color_style_var = (255, 255, 255) is white

def pin_name(pnt, data, headers, geo_index, description_location_var_name, scale_var, color_var, color_style_var):
	names = []

	for i in range(len(headers)):
		if description_location_var_name == headers[i]:
			location_num = i
	for j in range(len(data)):
		names.append(data[j][location_num])
	pnt.name = names[geo_index - 1]
	pnt.style.labelstyle.scale = scale_var

	if int(color_var) == 1:
		color_code = color_style_var
	else:
		color_code = "(255, 255, 255)"
	rgb_value = color_code.split(", ")
	r = rgb_value[0].split("(")
	r_value = r[1]
	g_value = rgb_value[1]
	b = rgb_value[2].split(")")
	b_value = b[0]
	pnt.style.labelstyle.color = simplekml.Color.rgb(int(r_value), int(g_value), int(b_value))

	return pnt
