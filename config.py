#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite://:memory:'
    SECRET_KEY = 'EGzBS6U4g9WB_Ob9bgzuOyO0p'
	
class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    
