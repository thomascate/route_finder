#!/usr/bin/env python

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import ujson as json
import logging
from pprint import pprint

#configuration
logging.basicConfig(filename='rs.api.log',level=logging.DEBUG)

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
