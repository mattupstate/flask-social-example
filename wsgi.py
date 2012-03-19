from app import create_app
print 'creating app'
application = create_app()

if __name__ == '__main__':
    application.run()