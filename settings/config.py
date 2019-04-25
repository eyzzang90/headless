# import config_local
# import config_real
import sys
import argparse
import json
import os


parser = argparse.ArgumentParser()
parser.add_argument('-env')
parser.add_argument('-imgSize')
args = parser.parse_args()

env = None
img_size = 0


def find_argv(argv, arg_name):
    result = ''
    val = None
    if argv.find(arg_name) > -1:
        arg_len = len(arg_name)
        val = argv[arg_len:]
        print('val::> ', val)

    if arg_name == '-env=':
        if val == 'local':
            # with open('settings/config_local.json') as config_file:
            abspath = os.path.dirname(os.path.abspath(__file__))
            with open(abspath+'/config_local.json') as config_file:
                conf = json.load(config_file)
                result = conf
        if val == 'real':
            abspath = os.path.dirname(os.path.abspath(__file__))
            with open(abspath+'/config_real.json') as config_file:
                conf = json.load(config_file)
                result = conf
    else:
        result = val
    print('end')
    return result


for i in range(1, len(sys.argv)):
    print('sys:::::', sys.argv[i])
    argv = str(sys.argv[i])

    if argv.find('-env=') > -1:
        env = find_argv(argv, '-env=')
    if argv.find('-imgSize=') > -1:
        img_size = find_argv(argv, '-imgSize=')

    print('env: ', env)
    print('img_size: ', img_size)
