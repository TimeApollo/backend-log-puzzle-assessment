#!/usr/bin/env python2
"""
Logpuzzle exercise

Copyright 2010 Google Inc.
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0

Google's Python Class
http://code.google.com/edu/languages/google-python-class/

Given an apache logfile, find the puzzle urls and download the images.

Here's what a puzzle url looks like:
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg
HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;
rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"

"""

import os
import re
import sys
import urllib
import argparse


def read_urls(filename):
    """Returns a list of the puzzle urls from the given log file,
    extracting the hostname from the filename itself.
    Screens out duplicate urls and returns the urls sorted into
    increasing order."""
    host_name = 'https://' + re.search(r'_(.+)', filename).group(1).strip()
    url_list = []
    with open(filename, 'r') as file:
        for line in file:
            url = re.search(r'\S+/puzzle/\S+', line)
            if url:
                url_list.append(host_name + url.group())
    pattern = re.search(r'-\w+-(\w+).jpg', url_list[0])
    if pattern:
        url_list = special_sort(url_list)
    else:
        url_list = sorted(set(url_list))
    return url_list


def special_sort(urls):
    """sorts by second word in -word-word.jpg pattern"""
    return sorted(set(urls),
                  key=lambda x: re.search(r'-\w+-(\w+).jpg', x).group(1))


def download_images(img_urls, dest_dir):
    """Given the urls already in the correct order, downloads
    each image into the given directory.
    Gives the images local filenames img0, img1, and so on.
    Creates an index.html in the directory
    with an img tag to show each local image file.
    Creates the directory if necessary.
    """
    file_paths = []
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for num, img_url in enumerate(img_urls):
        file_paths.append(create_img_file(img_url, dest_dir, num))
    create_html_file(file_paths, dest_dir)


def create_img_file(img_url, dest_dir, num):
    """creates image files (img + num) in dest_dir downloaded from img_url"""
    directory = os.path.abspath(dest_dir)
    file_name = 'img' + str(num)
    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w') as file:
        file.write(urllib.urlopen(img_url).read())

    return file_path


def create_html_file(file_paths, dest_dir):
    """creates html file that wraps img tags around all paths"""
    index_path = os.path.join(dest_dir, 'index.html')
    with open(index_path, 'w') as html:
        html.write('<html>\n<body>\n')
        for file_path in file_paths:
            html.write('<img src="{}">'.format(file_path))
        html.write('\n</body>\n</html>\n')


def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--todir',
                        help='destination directory for downloaded images')
    parser.add_argument('logfile', help='apache logfile to extract urls from')

    return parser


def main(args):
    """Parse args, scan for urls, get images from urls"""
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    img_urls = read_urls(parsed_args.logfile)

    if parsed_args.todir:
        download_images(img_urls, parsed_args.todir)
    else:
        print('\n'.join(img_urls))


if __name__ == '__main__':
    main(sys.argv[1:])
