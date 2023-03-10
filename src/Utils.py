#!/usr/bin/env python
# coding=utf-8

# This plugin is free software, you are allowed to
# modify it (if you keep the license),
# but you are not allowed to distribute/publish
# it without source code (this version and your modifications).
# This means you also have to distribute
# source code of your modifications.


import re
from .Debug import logger


temp_dir = "/var/volatile/tmp/tmdb/"


def cleanText(text):
	logger.debug("text 1: %s", text)
	cutlist = [
		'x264', '720p', '1080p', '1080i', 'PAL', 'GERMAN', 'ENGLiSH', 'WS', 'DVDRiP', 'UNRATED', 'RETAIL', 'Web-DL', 'DL', 'LD', 'MiC', 'MD', 'DVDR', 'BDRiP', 'BLURAY', 'DTS', 'UNCUT', 'ANiME',
		'AC3MD', 'AC3', 'AC3D', 'TS', 'DVDSCR', 'COMPLETE', 'INTERNAL', 'DTSD', 'XViD', 'DIVX', 'DUBBED', 'LINE.DUBBED', 'DD51', 'DVDR9', 'DVDR5', 'h264', 'AVC',
		'WEBHDTVRiP', 'WEBHDRiP', 'WEBRiP', 'WEBHDTV', 'WebHD', 'HDTVRiP', 'HDRiP', 'HDTV', 'ITUNESHD', 'REPACK', 'SYNC'
	]
	for word in cutlist:
		text = re.sub('(\_|\-|\.|\+)' + word + '(\_|\-|\.|\+)', '+', text, flags=re.I)  # noqa: W605, pylint: disable=W1401

	text = text.replace(":", " ").replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('+', '').replace(" Director's Cut", "").replace(" director's cut", "").replace("[Uncut]", "").replace("Uncut", "")
	text = " ".join(text.split())

	logger.debug("text 2: %s", text)
	if re.search('[Ss][0-9]+[Ee][0-9]+', text):
		text = re.sub('[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+', '', text, flags=re.S | re.I)
	text = re.sub(r'\(.*\)', '', text).rstrip()  # remove episode number from series, like "series name (234)"
	logger.debug("text 3: %s", text)
	return text


def checkText(text):
	# tuples indicate the bottom and top of the range, inclusive
	cjk_ranges = [
		(0x0600, 0x06FF),  # arabic
		(0x0750, 0x97FF),
		(0xAC00, 0xD7AF),  # hangul
		(0x4E00, 0x62FF),  # chinese
		(0x6300, 0x77FF),
		(0x7800, 0x8CFF),
		(0x8D00, 0x9FCC),
		(0x3400, 0x4DB5),
		(0x20000, 0x215FF),
		(0x21600, 0x230FF),
		(0x23100, 0x245FF),
		(0x24600, 0x260FF),
		(0x26100, 0x275FF),
		(0x27600, 0x290FF),
		(0x29100, 0x2A6DF),
		(0x2A700, 0x2B734),
		(0x2B740, 0x2B81D),
		(0x2B820, 0x2CEAF),
		(0x2CEB0, 0x2EBEF),
		(0x2F800, 0x2FA1F),
	]

	def is_cjk(char):
		char = ord(char)
		for bottom, top in cjk_ranges:
			if bottom <= char <= top:
				return True
		return False

	res = text
	if any(map(is_cjk, text)):
		res = ""
	return res
