#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 02:01:25 2019

@author: jiayilin
"""

import configparser
config = configparser.ConfigParser()
config['DEFAULT'] = {'foldLowerBound': '0.10', 'foldUpperBound': '0.37'}
with open('poker.ini', 'w') as configfile:
    config.write(configfile)