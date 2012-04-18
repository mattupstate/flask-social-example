import os
import sys
import urlparse
import yaml
from functools import wraps

from flask import (Flask as BaseFlask, Config as BaseConfig, 
                   render_template, flash)
from werkzeug import BaseResponse

class Config(BaseConfig):
    
    def from_heroku(self):
        # Register database schemes in URLs.
        for key in ['DATABSE_URL', 'SHARED_DATABASE_URL']:
            if key in os.environ:
                self['SQLALCHEMY_DATABASE_URI'] = os.environ[key]
                break

        for key in ['SECRET_KEY', 'GOOGLE_ANALYTICS_ID']:
            if key in os.environ:
                self[key] = os.environ[key]

        for key_prefix in ['TWITTER', 'FACEBOOK']:
            for key_suffix in ['key', 'secret']:
                ev = '%s_CONSUMER_%s' % (key_prefix, key_suffix.upper())
                if ev in os.environ:
                    social_key = 'SOCIAL_' + key_prefix
                    oauth_key = 'consumer_' + key_suffix
                    self[social_key]['oauth'][oauth_key] = ev

        
        #self['WEBASSETS_CACHE'] = 
    
    def from_yaml(self, root_path):
        env = os.environ.get('FLASK_ENV', 'DEVELOPMENT').upper()
        self['ENVIRONMENT'] = env.lower()
        
        for fn in ('app', 'credentials'):
            config_file = os.path.join(root_path, 'config', '%s.yml' % fn)
            
            try:
                with open(config_file) as f:
                    c = yaml.load(f)
                
                c = c.get(env, c)
                
                for key in c.iterkeys():
                    if key.isupper():
                        self[key] = c[key]
            except:
                pass
                    
                
class Flask(BaseFlask):
    """Extended version of `Flask` that implements custom config class
    and adds `register_middleware` method"""
    
    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return Config(root_path, self.default_config)
    
    def register_middleware(self, middleware_class):
        """Register a WSGI middleware on the application
        :param middleware_class: A WSGI middleware implementation
        """
        self.wsgi_app = middleware_class(self.wsgi_app)
        