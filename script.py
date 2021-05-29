#!/usr/bin/env python3
#author: Harshvardhan J. Pandit

# Script to extract privacy policy corpus into a temporal structure

# Needs Python3, tested in Python 3.9
# script should be executed in base folder of repo


OUTPUT_DIR = '../policy-corpus/'

import logging
from pathlib import Path
import os
import re
import subprocess

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
log_console_handler = logging.StreamHandler()
log_console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(funcName)s:%(lineno)d - %(message)s')
log_console_handler.setFormatter(formatter)
LOG.addHandler(log_console_handler)


# # To make all the necessary directories:
# for x in range(1990, 2022):
#     for y in 'AB':
#         try:
#             os.mkdir(os.path.join(OUTPUT_DIR, f'{x}_{y}'))
#         except FileExistsError:
#             pass


def get_files_from_directory(path='.', filetype='md'):
    '''1. File structure
    The folder is structured in a three-layered path leading from the starting
    1-3 letters of the website's name. However, this assumption is not
    guarenteed, since there might be a domain with less than 3 letters, and I'm
    not arsed to check it. So instead, recursively go down the tree, and build
    a path to anything that is a .md file. For html, swap this with .html.
    Once done, write them to a file for easier reuse later.
    '''
    LOG.debug(f'indexing {filetype} files from {path}')
    # files = sorted(str(x) for x in Path().rglob(f'*.{filetype}'))

    # FOR QUICKER TESTS:
    # Save file list to disk, and read that again.
    # 
    # Write file list to disk:
    # with open('./files.txt', 'w') as fd:
    #     for file in files:
    #         fd.write(f'{file}\n')
    # LOG.info('Wrote file list to files.txt')

    # Read saved filepaths:
    with open('./files.txt', 'r') as fd:
        files = [line.strip() for line in fd.readlines()]
    LOG.debug('Read file list from files.txt')

    # ARTIFICIAL LIMIT FOR TESTING
    LOG.info(f'found {len(files)} files')
    return files[:100]


def extract_file_history_from_git(filepath):
    '''2. Git history extraction
    Each file and the associated domain has its own special commit in the git
    history, where the metadata for when that file was changed (meaning the
    corresponding privacy policy had changed) is provided as a JSON dict.
    The command `git log --format="%H" <filepath>` will provide history of file.
    '''
    LOG.debug(f'extracting file history from git for {filepath}')
    result = subprocess.run(
        ['git', 'log', '--format="%H"', filepath],
        capture_output=True, text=True)
    result_output = [
        line.strip().strip('"')
        for line in result.stdout.split('\n')
        if len(line) > 5]
    LOG.debug(f'found {len(result_output)} commits for {filepath}')
    return result_output


def extract_interval_from_commit_message(commit):
    '''3. Git commit message extraction
    The command `git show -s --format="%b" <hash>` will provide 
    the commit message for hash without other info e.g. author, timestamp.
    An example of the output message:
    {
      "alexa_rank": NaN,
      "analysis_subcorpus": true,
      "categories": "business;informationtech",
      "char_count": 27489,
      "classifier_probability": 0.99,
      "cross_domain_homepage_redir": false,
      "flesch_ease": "difficult",
      "flesch_kincaid": 15.19,
      "homepage_snapshot_redirected_domain": "000domains.com",
      "homepage_snapshot_redirected_url": "https://web.archive.org...",
      "homepage_snapshot_url": "https://web.archive.org/web/...",
      "interval": "2019_A",  # <---------- TIME / YEAR / INTERVAL
      "link_text": "Privacy Policy",
      "parked_domain": false,
      "phase": "A",
      "policy_domain": "dotster.com",
      "policy_filetype": "html",
      "policy_snapshot_url": "https://web.archive.org/web/...",
      "policy_title": "Privacy Policy | Endurance International Group",
      "policy_url": "dotster.com/legal/legal_privacy.bml",
      "sha1": "9f2df85fac5aa07b90aae2ab6a9b9d12d924ad25",
      "simhash": 11227139907460965378,
      "simhash_updated": true,
      "site_hostname": "000domains.com",
      "site_url": "http://000domains.com",
      "smog": 16.97,
      "strict_updated": true,
      "timestamp": "20190629091058",
      "word_count": 4361,
      "year": 2019
    }
    
    '''
    commit_message = subprocess.run(
        ['git', 'show', '-s', '--format="%b"', commit], 
        capture_output=True, text=True).stdout
    re_interval = re.compile('"?interval"?:\s*"?([\w_]+)', re.MULTILINE)
    re_match = re_interval.search(commit_message)
    assert len(re_match.groups()) == 1
    interval = re_match.group(1)
    LOG.debug(f'commit {commit} has interval {interval}')
    return interval


def extract_file_to_interval_directory(filepath, commit, interval):
    '''4. Git file extraction
    `git show <commit>:<filepath> > <outputpath>/<interval>/<filepath>`
    '''
    outfile = os.path.join(OUTPUT_DIR, interval, os.path.basename(filepath))
    with open(outfile, 'w') as fd:
        subprocess.run(['git', 'show', f'{commit}:{filepath}'], stdout=fd)
    LOG.debug(f'wrote file {outfile}')
    return outfile


def run():
    files = get_files_from_directory()
    for file in files:
        commits = extract_file_history_from_git(file)
        for commit in commits:
            interval = extract_interval_from_commit_message(commit)
            extract_file_to_interval_directory(file, commit, interval)


if __name__ == '__main__':
    run()
