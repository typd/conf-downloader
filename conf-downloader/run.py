#!/usr/bin/env python
import os
import traceback
import argparse
#from subprocess import PIPE, Popen, call
from xml.dom import minidom

import requests
#import youtube_dl
from basicplib.util.logger import create_default_logger 
from basicplib.util.fileutil import convert_to_valid_path

DATA_ROOT = 'data'

def main():
    logger = create_default_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', dest='url', help='conf rss url')
    parser.add_argument('-n', dest='name', help='conf name')
    args = parser.parse_args()
    rss_url = args.url
    conf = args.name
    logger.info('================')
    logger.info('conf: {0}'.format(conf))
    logger.info('url : {0}'.format(rss_url))
    logger.info('----------------')
    logger.info(rss_url)
    req = requests.get(rss_url)
    xml = minidom.parseString(req.text)
    items = xml.getElementsByTagName('item')
    logger.info('got talks: {0}'.format(len(items)))
    folder = os.path.join(DATA_ROOT, conf)
    if not os.path.exists(folder): 
        os.makedirs(folder)
    exist_files = files_in(folder)
    logger.info('----------------')
    logger.info('downloaded files:')
    logger.info('\n'.join(exist_files))
    logger.info('----------------')
    index = 0
    for item in items:
        index += 1
        download_talk(logger, folder, exist_files, item, index)
    logger.info('================')

def files_in(dir):
    files = []
    for f_or_d in os.listdir(dir):
        path = os.path.join(dir, f_or_d)
        if os.path.isdir(path):
            files += files_in(path)
        else:
            files += [f_or_d]
    return files

def download_talk(logger, folder, exist_files, item, index):
    title = get_text(get_child_node(item, 'title'))
    enclosure = get_child_node(item, 'enclosure')
    url = enclosure.getAttribute('url')
    vtype = enclosure.getAttribute('type').replace('video/', '')
    logger.info('--------')
    logger.info('title: {0}'.format(title))
    logger.info('url  : {0}'.format(url))
    logger.info('type : {0}'.format(vtype))
    file_name = convert_to_valid_path(
            title.replace(' ', '_').replace(os.path.sep, '-'), '-') +\
            '.' + vtype
    path = os.path.join(folder, file_name)
    if file_name in exist_files:
        logger.info('  skip as file is downloaded already')
    else:
        logger.info('  path : {0}'.format(path))
        logger.info('  downloading from {0}'.format(url))
        """
        args = ['youtube-dl', '-o', path, '"{0}"'.format(url)]
        logger.info('    download with {0}'.format(args))
        proc = Popen(args, shell=False, stderr=PIPE)
        for line in iter(proc.stderr.readline, ""):
            if line:
                logger.info('    [output] %s', line.rstrip())
        result = proc.wait()
        """
        cmd = 'youtube-dl -o {0} "{1}"'.format(path, url)
        logger.info('    executing: {0}'.format(cmd))
        try:
            os.system(cmd)
            logger.info('  download succeed')
        except Exception as ex:
            logger.info('  download failed')
            logger.info('{0} \n {1}'.format(str(ex), traceback.format_exc()))

def get_child_node(node, tag):
    return node.getElementsByTagName(tag)[0]

def get_text(node):
    if node.nodeType == node.TEXT_NODE:
        return node.nodeValue
    return node.childNodes[0].nodeValue

if __name__ == '__main__':
    main()
