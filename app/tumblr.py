import tumblpy

config = {
    'id': 'tumblr',
    'name': 'Tumblr',
    'install': 'pip install python-tumblpy',
    'module': 'app.tumblr',
    'request_token_url': 'http://www.tumblr.com/oauth/request_token',
    'access_token_url': 'http://www.tumblr.com/oauth/access_token',
    'authorize_url': 'http://www.tumblr.com/oauth/authorize',
}

def get_api(connection, **kwargs):
    return tumblpy.Tublpy(app_key = kwargs.get('consumer_key'),
                          app_secret = kwargs.get('consumer_secret'),
                          oauth_token = connection.access_token,
                          oauth_token_secret = connection.secret
                          )

def get_provider_user_id(response, **kwargs):
    if response:
        t = tumblpy.Tublpy(app_key = kwargs.get('consumer_key'),
                              app_secret = kwargs.get('consumer_secret'),
                              oauth_token = response['access_token'],
                              oauth_token_secret = response['secret']
                              )
        user = t.post('user/info')
        return user['user']['name']
    return None

def get_connection_values(response, **kwargs):
    if not response:
        return None
    
    t = tumblpy.Tublpy(app_key = kwargs.get('consumer_key'),
                          app_secret = kwargs.get('consumer_secret'),
                          oauth_token = response['access_token'],
                          oauth_token_secret = response['secret']
                          )
    user = t.post('user/info')
    return {
        provider_id=config['id'],
        provider_user_id=str(user['user']['name']),
        access_token=response['access_token'],
        secret=response['secret'],
        display_name=user['user']['name'],
        profile_url=None,
        image_url=None,
        } 