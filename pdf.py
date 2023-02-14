import binascii
import logging
import logging.handlers

log_update = logging.getLogger('snowdeer_log')
log_update.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] (%(filename)s:%(lineno)d) > %(message)s')

fileHandler = logging.FileHandler('./log/log.txt', encoding='utf-8')
streamHandler = logging.StreamHandler()

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

log_update.addHandler(fileHandler)
log_update.addHandler(streamHandler)

filename = 'pdf/test.pdf'
with open(filename, 'rb') as f:
    content = f.read()

hex = binascii.hexlify(content)

log_update.debug(binascii.hexlify(content))
