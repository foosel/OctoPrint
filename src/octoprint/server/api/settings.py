# coding=utf-8
__author__ = "Gina Häußge <osd@foosel.net>"
__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'

import logging

from flask import request, jsonify

from octoprint.settings import settings

from octoprint.server import restricted_access, admin_permission
from octoprint.server.api import api

# Setting helpers
def setCura(data):
	s = settings()
	cura = data.get("cura", None)
	if cura:
		path = cura.get("path")
		if path:
			s.set(["cura", "path"], path)

		config = cura.get("config")
		if config:
			s.set(["cura", "config"], config)

		# Enabled is a boolean so we cannot check that we have a result
		enabled = cura.get("enabled")
		s.setBoolean(["cura", "enabled"], enabled)

def setLog(data):
	s = settings()
	oldLog = s.getBoolean(["serial", "log"])
	if "log" in data["serial"].keys():
		s.setBoolean(["serial", "log"], data["serial"]["log"])
	if oldLog and not s.getBoolean(["serial", "log"]):
		# disable debug logging to serial.log
		logging.getLogger("SERIAL").debug("Disabling serial logging")
		logging.getLogger("SERIAL").setLevel(logging.CRITICAL)
	elif not oldLog and s.getBoolean(["serial", "log"]):
		# enable debug logging to serial.log
		logging.getLogger("SERIAL").setLevel(logging.DEBUG)
		logging.getLogger("SERIAL").debug("Enabling serial logging")


@api.route("/settings", methods=["GET"])
def getSettings():
	s = settings()
	return jsonify(s.clientSettings())


@api.route("/settings", methods=["POST"])
@restricted_access
@admin_permission.require(403)
def setSettings():
	if "application/json" in request.headers["Content-Type"]:
		data = request.json
		s = settings()

		setLog(data)
		if "api" in data.keys():
			if "enabled" in data["api"].keys(): s.set(["api", "enabled"], data["api"]["enabled"])
			if "key" in data["api"].keys(): s.set(["api", "key"], data["api"]["key"], True)

		if "appearance" in data.keys():
			if "name" in data["appearance"].keys(): s.set(["appearance", "name"], data["appearance"]["name"])
			if "color" in data["appearance"].keys(): s.set(["appearance", "color"], data["appearance"]["color"])

		if "printer" in data.keys():
			if "movementSpeedX" in data["printer"].keys(): s.setInt(["printerParameters", "movementSpeed", "x"], data["printer"]["movementSpeedX"])
			if "movementSpeedY" in data["printer"].keys(): s.setInt(["printerParameters", "movementSpeed", "y"], data["printer"]["movementSpeedY"])
			if "movementSpeedZ" in data["printer"].keys(): s.setInt(["printerParameters", "movementSpeed", "z"], data["printer"]["movementSpeedZ"])
			if "movementSpeedE" in data["printer"].keys(): s.setInt(["printerParameters", "movementSpeed", "e"], data["printer"]["movementSpeedE"])
			if "invertAxes" in data["printer"].keys(): s.set(["printerParameters", "invertAxes"], data["printer"]["invertAxes"])
			if "numExtruders" in data["printer"].keys(): s.setInt(["printerParameters", "numExtruders"], data["printer"]["numExtruders"])
			if "extruderOffsets" in data["printer"].keys(): s.set(["printerParameters", "extruderOffsets"], data["printer"]["extruderOffsets"])
			if "bedDimensions" in data["printer"].keys(): s.set(["printerParameters", "bedDimensions"], data["printer"]["bedDimensions"])

		if "webcam" in data.keys():
			if "streamUrl" in data["webcam"].keys(): s.set(["webcam", "stream"], data["webcam"]["streamUrl"])
			if "snapshotUrl" in data["webcam"].keys(): s.set(["webcam", "snapshot"], data["webcam"]["snapshotUrl"])
			if "ffmpegPath" in data["webcam"].keys(): s.set(["webcam", "ffmpeg"], data["webcam"]["ffmpegPath"])
			if "bitrate" in data["webcam"].keys(): s.set(["webcam", "bitrate"], data["webcam"]["bitrate"])
			if "watermark" in data["webcam"].keys(): s.setBoolean(["webcam", "watermark"], data["webcam"]["watermark"])
			if "flipH" in data["webcam"].keys(): s.setBoolean(["webcam", "flipH"], data["webcam"]["flipH"])
			if "flipV" in data["webcam"].keys(): s.setBoolean(["webcam", "flipV"], data["webcam"]["flipV"])

		if "feature" in data.keys():
			if "gcodeViewer" in data["feature"].keys(): s.setBoolean(["gcodeViewer", "enabled"], data["feature"]["gcodeViewer"])
			if "temperatureGraph" in data["feature"].keys(): s.setBoolean(["feature", "temperatureGraph"], data["feature"]["temperatureGraph"])
			if "waitForStart" in data["feature"].keys(): s.setBoolean(["feature", "waitForStartOnConnect"], data["feature"]["waitForStart"])
			if "alwaysSendChecksum" in data["feature"].keys(): s.setBoolean(["feature", "alwaysSendChecksum"], data["feature"]["alwaysSendChecksum"])
			if "sdSupport" in data["feature"].keys(): s.setBoolean(["feature", "sdSupport"], data["feature"]["sdSupport"])
			if "sdAlwaysAvailable" in data["feature"].keys(): s.setBoolean(["feature", "sdAlwaysAvailable"], data["feature"]["sdAlwaysAvailable"])
			if "swallowOkAfterResend" in data["feature"].keys(): s.setBoolean(["feature", "swallowOkAfterResend"], data["feature"]["swallowOkAfterResend"])
			if "repetierTargetTemp" in data["feature"].keys(): s.setBoolean(["feature", "repetierTargetTemp"], data["feature"]["repetierTargetTemp"])

		if "serial" in data.keys():
			if "autoconnect" in data["serial"].keys(): s.setBoolean(["serial", "autoconnect"], data["serial"]["autoconnect"])
			if "port" in data["serial"].keys(): s.set(["serial", "port"], data["serial"]["port"])
			if "baudrate" in data["serial"].keys(): s.setInt(["serial", "baudrate"], data["serial"]["baudrate"])
			if "timeoutConnection" in data["serial"].keys(): s.setFloat(["serial", "timeout", "connection"], data["serial"]["timeoutConnection"])
			if "timeoutDetection" in data["serial"].keys(): s.setFloat(["serial", "timeout", "detection"], data["serial"]["timeoutDetection"])
			if "timeoutCommunication" in data["serial"].keys(): s.setFloat(["serial", "timeout", "communication"], data["serial"]["timeoutCommunication"])
			if "timeoutTemperature" in data["serial"].keys(): s.setFloat(["serial", "timeout", "temperature"], data["serial"]["timeoutTemperature"])
			if "timeoutSdStatus" in data["serial"].keys(): s.setFloat(["serial", "timeout", "sdStatus"], data["serial"]["timeoutSdStatus"])

		if "folder" in data.keys():
			if "uploads" in data["folder"].keys(): s.setBaseFolder("uploads", data["folder"]["uploads"])
			if "timelapse" in data["folder"].keys(): s.setBaseFolder("timelapse", data["folder"]["timelapse"])
			if "timelapseTmp" in data["folder"].keys(): s.setBaseFolder("timelapse_tmp", data["folder"]["timelapseTmp"])
			if "logs" in data["folder"].keys(): s.setBaseFolder("logs", data["folder"]["logs"])

		if "temperature" in data.keys():
			if "profiles" in data["temperature"].keys(): s.set(["temperature", "profiles"], data["temperature"]["profiles"])

		if "terminalFilters" in data.keys():
			s.set(["terminalFilters"], data["terminalFilters"])

		if "system" in data.keys():
			if "actions" in data["system"].keys(): s.set(["system", "actions"], data["system"]["actions"])
			if "events" in data["system"].keys(): s.set(["system", "events"], data["system"]["events"])

		setCura(data)

		# TODO after setting all vals generically, call s.setUserDirs()
		s.save()

	return getSettings()
