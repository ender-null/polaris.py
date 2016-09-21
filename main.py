from polaris import utils, types, loader, bot
from multiprocessing import Lock
import logging, time

logging.info('Looking for bot configurations in "bots" folder...')
botlist = loader.get_bots()

loader.setup()

try:
    for bot in botlist:
        logging.info('Initializing [%s] bot...' % bot.name)
        bot.start()

    while True:
        exited = 0
        for bot in botlist:
            if not bot.started:
                exited += 1
            time.sleep(1)
        
        if exited == len(botlist):
            logging.info('All bots have exited, finishing.')
            break

except KeyboardInterrupt:
    for bot in botlist:
        logging.info('Exiting [%s] bot...' % bot.name)
