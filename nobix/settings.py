# -*- coding: utf-8 -*-

"""
    nobix.settings
    ~~~~~~~~~~~~~~

    :copyright: 2012 by Augusto Roccasalva <augusto@rocctech.com.ar>
    :license: BSD, see LICENSE file for more details.
"""

import os
import sys
from ConfigParser import ConfigParser

_home = os.environ.get('HOME', '/')
xdg_data_home = os.environ.get('XDG_DATA_HOME', os.path.join(_home, '.local', 'share'))
xdg_config_home = os.environ.get('XDG_CONFIG_HOME', os.path.join(_home, '.config'))
xdg_config_dirs = [xdg_data_home] + os.environ.get('XDG_CONFIG_DIRS', '/etc/xdg').split(':')


def get_save_config_path(*resource):
    if not resource:
        resource = [XDG_CONF_RESOURCE]
    resource = os.path.join(*resource)
    assert not resource.startswith('/')
    path = os.path.join(xdg_config_home, resource)
    if not os.path.isdir(path):
        os.makedirs(path, 448) # 0o700
    return path

CONF_SECTION = "nobix"
XDG_CONF_RESOURCE = "nobix"
CONF_FILE_NAME = "nobix.cfg"


def load_config():
    from os.path import join, isdir

    cparser = ConfigParser()
    try:
        cparser.read([
            join(cdir, XDG_CONF_RESOURCE, CONF_FILE_NAME)
            for cdir in xdg_config_dirs if isdir(cdir)])

        if cparser.has_section(CONF_SECTION):
            conf_dict.update(dict(cparser.iterms(CONF_SECTION)))
    except:
       pass
