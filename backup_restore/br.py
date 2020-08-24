import os
import platform
import sys
import textwrap
import logging
from configparser import ConfigParser
try :
    import argparse
except ImportError:
    os.system('pip install --user argparser')


logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s', )


operating_sytem = platform.system()
machine_id = platform.node()
argument_parser = argparse.ArgumentParser(
    prog='br.py',
    formatter_class=argparse.RawTextHelpFormatter,
    description='Backup and restore',
    usage='br ',
    epilog=textwrap.dedent(
        '''
        comming soon
        '''
    )
)

argument_parser.add_argument('-l', '--load',
                             help='load setting name',
                             )
argument_parser.add_argument('-n', '--name',
                             help='get setting name',
                             )
argument_parser.add_argument('-r', '--restore',
                             action='store_true',
                             help='reverse backup',
                             )
argument_parser.add_argument('-s', '--source',
                            help='source location',
                            )
argument_parser.add_argument('-d', '--destination',
                            help='destination location',
                            )


parsed_arg = argument_parser.parse_args()
config = ConfigParser()
load = vars(parsed_arg).get('load')
rst = vars(parsed_arg).get('restore')
name = vars(parsed_arg).get('name')      
src = vars(parsed_arg).get('source')
dst = vars(parsed_arg).get('destination')

if name and src and dst:
    if not machine_id in config:
        logging.debug("profile created")
        config[machine_id]={}
    logging.info('save name %s' % name)
    src_name = 'src_'+name
    dst_name = 'dst_'+name
    config[machine_id]['name'] = name
    config[machine_id][src_name] = src
    config[machine_id][dst_name] = dst
    logging.debug('writting br.ini')
    with open('br.ini', 'w') as configfile:
        config.write(configfile)

elif load:
    config = ConfigParser()
    config.read('br.ini')
    logging.info('load name %s' % load)

    src_name = config[machine_id]['src_'+load]
    dst_name = config[machine_id]['dst_'+load]
    tool='robocopy' if operating_sytem=='Windows' else 'rsync'

    if rst:
        args = tool+' \"'+dst_name+'\" \"'+src_name+'\" /MIR'
    else:
        args = tool+' \"'+src_name+'\" \"'+dst_name+'\" /MIR'

    logging.debug('\nsrc\t= %s\ndst\t= %s\nrst?\t= %s\ntool\t= %s\nargs\t= %s ' 
        % (src_name, dst_name, rst, tool, args))

    try:
        os.system(args)
    except OSError as e:
        logging.error("error %s" %e)

else :
    logging.error('see help -h')
