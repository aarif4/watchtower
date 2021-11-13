import sys
from time import sleep
from utils.config import config
from utils.logger import Logger
from core.gallery import gallery
from utils.mode import MODE


def default(cfg_dict, logger):
    # call the gallery once
    logger.info('running "default"')
    galla = gallery(cfg_dict)
    galla.run()

def service(cfg_dict, logger):
    # routinely call the gallery to evaluate the user's config
    logger.info('running "service"')
    TIMEOUT_SEC = 60
    
    galla = gallery(cfg_dict)
    try:
        while True:
            galla.run()
            sleep(TIMEOUT_SEC)
    except KeyboardInterrupt:
        pass # TODO: should probably exit all of the scrapers safely

def app(cfg_dict, logger):
    # run the front end and fill it out with the current user config
    logger.info('running "app"')
    pass

def gui(cfg_dict, logger):
    # run the front end and wait for the user to decide which config file to load
    # make sure to override the mode to gui
    logger.info('running "gui"')
    pass

if __name__ == "__main__":
    # read the configuration file
    logger = Logger('main')
    logger.info('firsst main logger')
    logger2 = Logger('main2')
    logger2.info('second main logger. should happen once')
    
    # TODO: Get user config from input args
    cfg = config(sys.argv[1], sys.argv[2])
    cfg_dict = cfg.get_dict()

    if cfg.mode == MODE.DEFAULT:
        default(cfg_dict, logger)

    if cfg.mode == MODE.SERVICE:
        service(cfg_dict, logger)

    if cfg.mode == MODE.APP:
        app(cfg_dict, logger)

    if cfg.mode == MODE.GUI:
        gui(cfg_dict, logger)
