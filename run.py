from settings import Settings
import optimize
import json

if __name__ == '__main__':

    log = Settings.get( 'Logger')()
    
    try:
        environment = Settings.get('LiveEnvironment')()
        environment.run()

    except BaseException as e:

        log.error(e)
        log.info(e)
