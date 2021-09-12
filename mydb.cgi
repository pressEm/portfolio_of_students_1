#!/usr/bin/python3

import sys
import os

from app import app

from wsgiref.handlers import CGIHandler

CGIHandler().run(app)
