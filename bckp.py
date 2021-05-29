#!/usr/bin/env python3
#author: Harshvardhan J. Pandit

# Script to extract privacy policy corpus into a temporal structure

# Needs Python3, tested in Python 3.9
# script should be executed in base folder of repo

# ---
# 1. File structure
# The folder is structured in a three-layered path leading from the starting
# 1-3 letters of the website's name. However, this assumption is not
# guarenteed, since there might be a domain with less than 3 letters, and I'm
# not arsed to check it. So instead, recursively go down the tree, and build
# a path to anything that is a .md file. For html, swap this with .html.
# Once done, write them to a file for easier reuse later.

# /-- A. Re-run filepath item and save to file
# from pathlib import Path

# files = sorted(str(x) for x in Path().rglob('*.md'))
# files_sample = files[:100]
# print(files_sample)
# with open('./files.txt', 'w') as fd:
#     for file in files:
#         fd.write(f'{file}\n')
# --/

# /-- B. Read saved filepaths
with open('./files.txt', 'r') as fd:
    files = [line.strip() for line in fd.readlines()]
    files_sample = files[:100]
# ---

# 2. Git history extraction
# Each file and the associated domain has its own special commit in the git
# history, where the metadata for when that file was changed (meaning the
# corresponding privacy policy had changed) is provided as a JSON dict.
# The command `git log --format="%H" <filepath>` will provide history of file.

import subprocess

file = files_sample[0]
# /-- A. Re-run history extraction from git
# result = subprocess.run(
#     ['git', 'log', '--format="%H"', file], capture_output=True, encoding='utf-8')
# result_output = [
#     line.strip().strip('"') 
#     for line in result.stdout.split('\n') 
#     if len(line) > 5]
# with open('./file-history.txt', 'w') as fd:
#     for line in result_output:
#         fd.write(f'{line}\n')
# --/

# /-- B. Re-use data saved to file
with open('./file-history.txt', 'r') as fd:
    file_history = [line.strip() for line in fd.readlines()]
# print(file_history)
# --/

# ---
# 3. Git commit message extraction
# The command `git show -s --format="%b" <hash>` will provide 
# the commit message for hash without other info e.g. author, timestamp.
# An example of the output message:
# {
#   "alexa_rank": NaN,
#   "analysis_subcorpus": true,
#   "categories": "business;informationtech",
#   "char_count": 27489,
#   "classifier_probability": 0.99,
#   "cross_domain_homepage_redir": false,
#   "flesch_ease": "difficult",
#   "flesch_kincaid": 15.19,
#   "homepage_snapshot_redirected_domain": "000domains.com",
#   "homepage_snapshot_redirected_url": "https://web.archive.org/web/20190102122452id_/http://www.000domains.com/",
#   "homepage_snapshot_url": "https://web.archive.org/web/20190102122452id_/http%3A//000domains.com",
#   "interval": "2019_A",
#   "link_text": "Privacy Policy",
#   "parked_domain": false,
#   "phase": "A",
#   "policy_domain": "dotster.com",
#   "policy_filetype": "html",
#   "policy_snapshot_url": "https://web.archive.org/web/20190629091058id_/http%3A//www.dotster.com/legal/legal_privacy.bml",
#   "policy_title": "Privacy Policy | Endurance International Group",
#   "policy_url": "dotster.com/legal/legal_privacy.bml",
#   "sha1": "9f2df85fac5aa07b90aae2ab6a9b9d12d924ad25",
#   "simhash": 11227139907460965378,
#   "simhash_updated": true,
#   "site_hostname": "000domains.com",
#   "site_url": "http://000domains.com",
#   "smog": 16.97,
#   "strict_updated": true,
#   "timestamp": "20190629091058",
#   "word_count": 4361,
#   "year": 2019
# }
# 
# From these, currently, we need only the year interval, which is x['interval']

OUTPUT_DIR = '../policy-corpus/'
import os

for file_commit in file_history:
    result = subprocess.run(
        ['git', 'show', '-s', '--format="%b"', file_commit], 
        capture_output=True, text=True)
    file_commit_message = result.stdout
    import re
    re_interval = re.compile('"?interval"?:\s*"?([\w_]+)', re.MULTILINE)
    file_commit_interval = re_interval.search(file_commit_message).group(1)
    print(file_commit_interval)

def extract_file_to_interval(filepath, commit, interval):
    outfile = os.path.join(OUTPUT_DIR, interval, os.path.basename(filepath))
    with open(outfile, 'w') as fd:
        subprocess.run(['git', 'show', f'{commit}:{file}'], stdout=fd)

# ---
# 4. Git file extraction
# command: `git show <commit>:<filepath> > <outputpath>/<interval>/<filepath>`
