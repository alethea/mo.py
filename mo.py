#!/usr/bin/env python2.7

import os
import shutil
import argparse
import mutagen

def process_name(name, mode, max_length=None):
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
    if mode == 'unix' or mode == 'mixed':
        return unix

def main():
    parser = argparse.ArgumentParser(prog="MO",
            description="Organize music files into directories.")
    mode_group = parser.add_mutually_exclusive_group()
    parser.add_argument('sources', metavar='SOURCE', nargs="+",
            help='Files to examine')
    parser.add_argument('target', metavar='TARGET',
            help='Destination for new directory structure')
    parser.set_defaults(mode='unix', max_length=None)
    mode_group.add_argument('-c', '--clean', dest='mode',
            action='store_const', const='clean', help='Strip \
                    non-alphanumeric characters from filenames, leave \
                    whitespace and uppercase characters')
    mode_group.add_argument('-s', '--shorten', dest='mode',
            action='store_const', const='short', help='Shorten filenames to \
                    lowercase initials')
    mode_group.add_argument('-m', '--mixed', dest='max_length', type=int,
            metavar='LENGTH', help='Shorten filenames if longer than \
                    LENGTH, use UNIX names otherwise')

    args = parser.parse_args()
    if args.max_length != None:
        args.mode = 'mixed'

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
        directory = os.path.join(args.target, 
                process_name(artist, args.mode, args.max_length), 
                process_name(album, args.mode, args.max_length))
        directories.add(directory)
        filename = ('{0:02}'.format(track) + 
                process_name(title, args.mode, args.max_length) + 
                os.path.splitext(source)[1].lower())
        filepairs.append((source, os.path.join(directory, filename)))

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    for filepair in filepairs:
        shutil.copy(filepair[0], filepair[1])

if __name__ == '__main__':
    main()
