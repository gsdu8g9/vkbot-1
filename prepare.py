import os
import sys
import codecs
import importlib
import fcntl
import time
from args import args
import accounts
import log
import config
from vkapi import vk_api

os.environ['LC_ALL'] = 'ru_RU.utf-8'
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
login = config.get('login.login')
password = config.get('login.password')

def availableScripts():
    print('Available scripts:', ', '.join(i[:-3] for i in os.listdir('scripts') if i.endswith('.py') and not i.startswith('__')))
    sys.exit()

if args['script'] is None:
    availableScripts()

if args['script']:
    if not args['script'].replace('_', '').isalpha():
        print('Invalid script')
        availableScripts()
    log.script_name = args['script'].lower()
    try:
        main = importlib.import_module('scripts.' + args['script'].lower()).main
    except ImportError:
        print('Invalid script')
        availableScripts()
    v = vk_api(login, password)
    main(v, args['args'])
    v.sync()
    sys.exit()

pid_file = accounts.getFile('inf.pid')
lock_file = accounts.getFile('inf.lock')
fp = open(lock_file, 'w')
single = False
for i in range(100):
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        time.sleep(5)
    else:
        single = True
        break
if not single:
    sys.exit(1)
with open(pid_file, 'w') as f:
    f.write(str(os.getpid()))

log.info('Starting vkbot, pid ' + str(os.getpid()))