
from flask.ext.assets import Environment, Bundle

def init_assets(app):
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

    assets = Environment(app)
    assets.manifest = 'cache' if not app.debug else False
    assets.cache = not app.debug
    #assets.debug = app.config['ENVIRONMENT'] == 'development'
    assets.debug = app.debug

    assets.register('js_libs', js_libs)
    assets.register('js_main', js_main)
    assets.register('css_main', css_main)
