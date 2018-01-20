# -*- coding: utf-8 -*-

import sys
import time
import urllib2
import smtplib
import argparse
import logging


def main():
    # Set the arguments for the parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="The program compares a given site"
        "to its already stored state"
        "with the help of predefined keywords.\n"
        "If the site is yet to be stored in a file,"
        "it will be downloaded first, then the program regularly\n"
        "checks on it if it has changed or not.")
    parser.add_argument(
        "-u",
        metavar='URL',
        nargs='?',
        help="specify the site's url that you want to download"
        "from (default: %(default)s)",
        default='google.com',
        dest='url')
    parser.add_argument(
        "-l",
        metavar=('file1', 'file2'),
        nargs=2,
        help="mail mode, if there is a change,"
        "it will send an email address\n"
        "- file1 has to be specified, it can be an email, or a file\n"
        "- file2 has to be specified,"
        "it is the file that stores the credentials",
        dest='mail')
    parser.add_argument(
        "-k",
        metavar='file',
        nargs='?',
        help="keyword file, default is a list (%(default)s)",
        dest='keywordfile',
        default=[[' ']],
        const=[[' ']])
    parser.add_argument(
        "-t",
        metavar='SEC',
        help="set waiting time in seconds (default: %(default)s seconds)",
        type=int,
        default=5,
        dest='time')
    parser.add_argument(
        "-v",
        help="enable verbose output",
        action="store_true",
        dest='verbose')
    args = parser.parse_args()

    # If args.mail exists, then check if their values are valid
    if args.mail:
        _get_recipients(args.mail[0])
        _get_credentials(args.mail[1])

    # Set logging message format, redirect it to stdout
    if args.verbose:
        root = logging.getLogger()
        root.setLevel(logging.INFO)

        sout = logging.StreamHandler(sys.stdout)
        sout.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        sout.setFormatter(formatter)

        root.addHandler(sout)

    # Start logging with given details
    logging.info('PROGRAM START')
    logging.info('Delay: %s second(s), URL: %s, Wordlist: %s' %
                 (args.time, args.url, args.keywordfile))
    if args.mail:
        logging.info('Recipients: %s, Credentials: %s\n' %
                     (args.mail[0], args.mail[1]))
    else:
        logging.info('Recipients: not set, Credentials: not set\n')

    # Check for change, and send an email
    # if change was detected every x seconds
    changed = False
    while not changed:
        logging.info('Checking (before delay)')
        changed = check(_get_site(args.url, False), _get_site(
            args.url, True), _get_keywordlist(args.keywordfile))
        logging.info('Check complete')
        if changed:
            break
        time.sleep(args.time)

    logging.info('Change detected')
    if args.mail:
        logging.info('Sending email')
        send_email(_get_recipients(
            args.mail[0]), _get_credentials(args.mail[1]))
        logging.info('Email sent')
    logging.info('PROGRAM END')


def send_email(recipients, credentials):
    gmail_user = credentials[0]
    gmail_pwd = credentials[1]
    FROM = credentials[0]
    TO = recipients
    SUBJECT = 'Site change'
    TEXT = 'A change was detected.'

    # Prepare message
    message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (
        FROM, ", ".join(TO), SUBJECT, TEXT)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
    except:
        logging.info('Failed to send the mail')


def check(siteurl, filename, wordlists):
    page = urllib2.urlopen(siteurl)

    try:
        with open(filename + '.html', 'rb') as file:
            fs = file.read().lower()
        ps = page.read().lower()

        # Compares the file and the page if they have the same amount of words
        # that is also in a wordlist.
        # Wordlists are separately evaluated,
        # so if the page has an extra word1, but one less word2,
        # the amount is the same, and the check doesn't trigger.
        # But if they are in a separate group, they are treated differently.
        different = any(sum(fs.count(word) for word in wordlists[i]) != sum(
            ps.count(word) for word in wordlists[i])
            for i in range(0, len(wordlists)))

        changetable = [sum(fs.count(word) for word in wordlists[i]) != sum(
            ps.count(word) for word in wordlists[i])
            for i in range(0, len(wordlists))]

        logging.info('Change table: [%s]' % ', '.join(map(str, changetable)))

        if (different):
            return True
    except IOError:
        with open(filename + '.html', 'wb') as file:
            file.write(page.read())
        logging.info('File created')

    return False


def _get_recipients(filename):
    try:
        with open(filename, 'rb') as file:
            return file.read().splitlines()
    except IOError:
        # This method will recieve a valid filename,
        # or an invalid filename that is not an email,
        # and an invalid filename that can also be an email,
        # therefore, it has to be checked which happened.
        # Opening the file is the default action.
        if '@' in filename:
            # Need to return a list format,
            # because the email would be received, but the
            # recipient email would be split into characters
            # that will be sent to the SMTP server
            return [filename]
        else:
            raise ValueError('Invalid recipient')


def _get_credentials(filename):
    try:
        with open(filename, 'rb') as file:
            return file.read().splitlines()
    except IOError:
        raise ValueError('Credential file is missing')


def _get_keywordlist(filename):
    try:
        with open(filename, 'rb') as file:
            return [wordlist.split(', ')
                    for wordlist in file.read().splitlines()]
    except IOError:
        raise ValueError('Keyword file is missing')
    except TypeError:
        return filename


def _get_site(siteurl, fileflag):
    if fileflag:
        if 'http://' == siteurl[:7]:
            return siteurl[7:]
        elif 'https://' == siteurl[:8]:
            return siteurl[8:]
        else:
            return siteurl
    else:
        if 'http://' == siteurl[:7]:
            return siteurl
        elif 'https://' == siteurl[:8]:
            return siteurl
        else:
            return 'http://' + siteurl


if __name__ == "__main__":
    main()
