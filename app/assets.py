
from flask.ext.assets import Bundle

from . import app, webassets

js_libs = Bundle("js/libs/jquery-1.7.1.min.js",
                 "js/libs/bootstrap.min.js",
                 filters="jsmin",
                 output="js/libs.js")

js_main = Bundle("js/src/main.js",
                 filters="jsmin",
                 output="js/main.js")

css_less = Bundle("css/src/styles.less",
                  filters="less",
                  output="css/styles.css",
                  debug=False)

css_main = Bundle(Bundle("css/bootstrap.min.css"),
                  css_less,
                  filters="cssmin",
                  output="css/main.css")


webassets.manifest = 'cache' if not app.debug else False
webassets.cache = not app.debug
webassets.debug = app.debug

webassets.register('js_libs', js_libs)
webassets.register('js_main', js_main)
webassets.register('css_main', css_main)
