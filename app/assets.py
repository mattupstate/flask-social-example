from flask.ext.assets import Environment, Bundle

def init_assets(app):    
    js_libs = Bundle("js/libs/jquery-1.7.1.min.js",
                     filters="jsmin", 
                     output="js/libs.js")
    
    js_main = Bundle("js/src/main.js",
                     filters="jsmin",
                     output="js/main.js")
    
    css_main = Bundle("css/src/main.less", 
                      filters="less", 
                      output="css/main.css", 
                      debug=False)
    
    assets = Environment(app)
    assets.cache = False
    assets.debug = app.config['ENVIRONMENT'] in ['development', 'staging']
    
    assets.register('js_libs', js_libs)
    assets.register('js_main', js_main)
    assets.register('css_main', css_main)
    