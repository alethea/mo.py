#!/usr/bin/env python2.7

import os
import shutil
import argparse
import mutagen

def process_name(name, mode, max_length=30):
    if mode == 'none':
        return unicode(name)
    splitnames = name.split()
    subnames = []
    for splitname in splitnames:
        subname = u''.join(char for char in splitname if char.isalnum())
        if len(subname) > 0:
            subnames.append(subname)
    if mode == 'clean':
        return u' '.join(subnames)
    unix = u'-'.join(subname.lower() for subname in subnames)
    if mode == 'short' or (mode == 'mixed' and len(unix) > max_length):
        return u''.join(subname.lower()[0] for subname in subnames)
    if mode == 'unix':
        return unix

def main():
    parser = argparse.ArgumentParser(
            description="Organize music files into directories.")
    parser.add_argument('sources', metavar='SOURCE', nargs="+",
            help="Files to examine")
    parser.add_argument('target', metavar='TARGET',
            help="Destination for new directory structure")

    args = parser.parse_args()

    directories = set()
    filepairs = list()

    for source in args.sources:
        metadata = mutagen.File(source, easy=True)
        if metadata == None:
            continue
        artist = metadata['artist'][0]
        album = metadata['album'][0]
        title = metadata['title'][0]
        track = int(metadata['tracknumber'][0])
        directory = os.path.join(args.target, artist, album)
        directories.add(directory)
        filename = '{0:02}'.format(track) + title + os.path.splitext(source)[1].lower()
        filepairs.append((source, os.path.join(directory, filename)))

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    for filepair in filepairs:
        shutil.copy(filepair[0], filepair[1])

if __name__ == '__main__':
    main()
