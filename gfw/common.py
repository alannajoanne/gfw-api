# Global Forest Watch API
# Copyright (C) 2013 World Resource Institute
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""This module supports common functions."""

import copy
import json
from hashlib import md5
import urllib
import urlparse

from appengine_config import runtime_config

#
# SHARED CONSTANTS/TEMPLATES
#
ALLOWED_DOMAINS = [
    'api-gateway-staging.globalforestwatch.org',
    'www.globalforestwatch.org', 'globalforestwatch.org',
    'staging.globalforestwatch.org', 'localhost:5000'
    'fires.globalforestwatch.org', 'www.fires.globalforestwatch.org',
    'commodities.globalforestwatch.org', 'www.commodities.globalforestwatch.org'
    'climate.globalforestwatch.org', 'www.climate.globalforestwatch.org',
    'data.globalforestwatch.org', 'www.data.globalforestwatch.org',
    'developers.globalforestwatch.org', 'www.developers.globalforestwatch.org',
    'blog.globalforestwatch.org', 'www.blog.globalforestwatch.org'
]
APP_VERSION = runtime_config.get('APP_VERSION')
APP_BASE_URL = runtime_config.get('APP_BASE_URL')
IS_DEV = runtime_config.get('IS_DEV')
CONTENT_TYPES = {
    'shp': 'application/octet-stream',
    'kml': 'application/vnd.google-earth.kmz',
    'svg': 'image/svg+xml',
    'csv': 'application/csv',
    'geojson': 'application/json',
    'json': 'application/json'
}
GCS_URL_TMPL = 'http://storage.googleapis.com/gfw-apis-analysis%s.%s'

def gfw_url(path, params={}):
    base_url = runtime_config.get('GFW_BASE_URL')

    url_parts = list(urlparse.urlparse(base_url))
    url_parts[2] = urlparse.urljoin(url_parts[2], path)

    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)

    return urlparse.urlunparse(url_parts)

#
# Helper Methods
#
def get_params_hash(params):
    return md5(json.dumps(params, sort_keys=True)).hexdigest()

def get_cartodb_format(gfw_media_type):
    """Return CartoDB format for supplied GFW custom media type."""
    tokens = gfw_media_type.split('.')
    if len(tokens) == 2:
        return 'json'
    else:
        return tokens[2].split('+')[0]
