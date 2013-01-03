#!/usr/bin/env python2.7
"""
MO

A simple utility to organize music files into directories based on tags.
Requires Python 2.7 and the Mutagen tagging library.
"""

import os
import shutil
import argparse
import mutagen

def main():
    parser = argparse.ArgumentParser(prog='MO',
            description='A simple utility to organize music files into \
                    directories based on tags.')
    parser.set_defaults(mode='unix', max_length=None, overwrite='no')

    overwrite_group = parser.add_mutually_exclusive_group()
    overwrite_group.add_argument('-f', '--force', dest='overwrite', 
            action='store_const', const='yes', help='overwrite existing \
                    files without prompting')
    overwrite_group.add_argument('-i', '--interactive', dest='overwrite',
            action='store_const', const='ask', help='ask before overwriting \
                    files')

    parser.add_argument('sources', metavar='SOURCE', nargs="+",
            help='files to examine')
    parser.add_argument('target', metavar='TARGET',
            help='destination for new directory structure')

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('-u', '--upper', dest='mode',
            action='store_const', const='clean', help='strip \
                    non-alphanumeric characters from filenames, leave \
                    whitespace and uppercase characters')
    mode_group.add_argument('-s', '--shorten', dest='mode',
            action='store_const', const='short', help='shorten filenames to \
                    its lowercase initials')
    mode_group.add_argument('-l', '--length', dest='max_length', type=int,
            help='shorten filenames if longer than LENGTH, use UNIX names \
                    otherwise')

    parser.add_argument('-t', '--format', help='format string for new \
            directory. Valid tags are {artist}, {album}, {title}, \
            {track}, {disc}, {year} Ex:' + repr(default_formats['unix']))

    args = parser.parse_args()
    if args.max_length != None:
        args.mode = 'mixed'
    if args.format == None:
        args.format = default_formats[args.mode]

    directories = set()
    filepairs = {}

    for source in args.sources:
        metadata = mutagen.File(source, easy=True)
        if metadata == None:
            continue
        tags = {
                'artist': process_name(' '.join(metadata.get('artist', 
                    ['Unknown'])), args),
                'album': process_name(' '.join(metadata.get('album',
                    ['Unknown'])), args),
                'title': process_name(' '.join(metadata.get('title',
                    ['Unknown'])), args),
                'track': process_number(metadata.get('tracknumber', [0])[0]),
                'disc': process_number(metadata.get('discnumber', [0])[0]),
                'year': str(process_number(metadata.get('date',
                    ['Unknown'])[0], 4))}
        ext = os.path.splitext(source)[1].lower()
        filename = args.format.format(**tags) + ext
        filepairs[source] = filename
        directories.add(os.path.dirname(filename))
        
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    for source, dest in filepairs.viewitems():
        if os.path.exists(dest) and args.overwrite != 'yes':
            if args.overwrite == 'no':
                parser.error('File exists: {0}'.format(dest))
            elif args.overwrite == 'ask':
                responce = None
                print('File exists: {0}'.format(dest))
                while responce != 'n' and responce != 'y':
                    responce = raw_input('Overwrite it? [y/n] ')
                if responce == 'n':
                    continue
        shutil.copy(source, dest)

def process_name(name, args):
    if args.mode == 'none':
        return unicode(name)
    splitnames = name.split()
    subnames = []
    for splitname in splitnames:
        subname = u''.join(char for char in splitname if char.isalnum())
        if len(subname) > 0:
            subnames.append(subname)
    if args.mode == 'clean':
        return u' '.join(subnames)
    unix = u'-'.join(subname.lower() for subname in subnames)
    if args.mode == 'short' or (args.mode == 'mixed' and 
            len(unix) > args.max_length):
        return u''.join(subname.lower()[0] for subname in subnames)
    if args.mode == 'unix' or args.mode == 'mixed':
        return unix

def process_number(number, length=None):
    if number == None or number == 'Unknown' or isinstance(number, int):
        return number
    digits = []
    found_digit = False
    for char in number:
        if char.isdigit():
            digits.append(char)
            found_digit = True
        elif found_digit:
            break
    if length != None and len(digits) != length:
        return 'Unknown'
    return int(''.join(digits))

default_formats = {
        'none': os.path.join('{artist}', '{album}', '{track:02} {title}'),
        'clean': os.path.join('{artist}', '{album}', '{track:02} {title}'),
        'short': os.path.join('{artist}', '{album}', '{track:02}{title}'),
        'mixed': os.path.join('{artist}', '{album}', '{track:02}-{title}'),
        'unix': os.path.join('{artist}', '{album}', '{track:02}-{title}')}

if __name__ == '__main__':
    main()

