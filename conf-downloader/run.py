#!/usr/bin/env python
import os
import traceback
import argparse
from subprocess import PIPE, Popen, call
from xml.dom import minidom

import requests
import youtube_dl
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
    logger.info('conf: {}'.format(conf))
    logger.info('url : {}'.format(rss_url))
    logger.info('----------------')
    logger.info(rss_url)
    req = requests.get(rss_url)
    xml = minidom.parseString(req.text)
    items = xml.getElementsByTagName('item')
    logger.info('got talks: {}'.format(len(items)))
    folder = os.path.join(DATA_ROOT, conf)
    if not os.path.exists(folder): 
        os.makedirs(folder)
    index = 0
    for item in items:
        index += 1
        download_talk(logger, folder, item, index)
    logger.info('================')

def download_talk(logger, folder, item, index):
    title = get_text(get_child_node(item, 'title'))
    enclosure = get_child_node(item, 'enclosure')
    url = enclosure.getAttribute('url')
    vtype = enclosure.getAttribute('type').replace('video/', '')
    logger.info('--------')
    logger.info('title: {}'.format(title))
    logger.info('url  : {}'.format(url))
    logger.info('type : {}'.format(vtype))
    file_name = convert_to_valid_path(
            title.replace(' ', '_').replace(os.path.sep, '-'), '-') +\
            '.' + vtype
    path = os.path.join(folder, file_name)
    logger.info('path : {}'.format(path))
    if os.path.exists(path):
        logger.info('  skip as file is downloaded already')
    else:
        logger.info('  downloading from {}'.format(url))
        """
        args = ['youtube-dl', '-o', path, '"{}"'.format(url)]
        logger.info('    download with {}'.format(args))
        proc = Popen(args, shell=False, stderr=PIPE)
        for line in iter(proc.stderr.readline, ""):
            if line:
                logger.info('    [output] %s', line.rstrip())
        result = proc.wait()
        """
        cmd = 'youtube-dl -o {} "{}"'.format(path, url)
        logger.info('    executing: {}'.format(cmd))
        try:
            os.system(cmd)
            logger.info('  download succeed')
        except Exception as ex:
            logger.info('  download failed')
            logger.info('{} \n {}'.format(str(ex), traceback.format_exc()))

def get_child_node(node, tag):
    return node.getElementsByTagName(tag)[0]

def get_text(node):
    if node.nodeType == node.TEXT_NODE:
        return node.nodeValue
    return node.childNodes[0].nodeValue

if __name__ == '__main__':
    main()