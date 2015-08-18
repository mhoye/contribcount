#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import Repository as Repository
from pygit2 import GIT_SORT_TIME as GIT_SORT_TIME
import sys
import time
from datetime import date
import datetime

if (len(sys.argv) == 1) or (len(sys.argv) > 4) or ("-?" == sys.argv[2]) or ("--help" == sys.argv[2]):
    print   "\nThis script determines contributor numbers over a range " +\
            "range of previous. It requires:\n" +\
            " - A list of locally-cloned git repositories (git submodules)\n"  +\
            " - A list of known employee email addresses\n" +\
           "Order of arguments is important:\n" +\
        "contrib-git.py [list of git repos] [list of email addrs] [number of months]\n"
    exit()

repos = list()

try:
    with open(sys.argv[2]) as r:
        repos = r.readlines()
except:
    print ('Could not read or interpret %s', sys.argv[2])
    exit -1

employees = list()

try:
    with open(sys.argv[3]) as e:
        employees = e.readlines()
except:
    print ('Could not read or interpret %s', sys.argv[3])
    exit -1
try:
    num_months = int(sys.argv[4])
except:
    print "That last thing has to be a positive integer."
    exit -1

res_emp = list()
res_vol = list()
res_tot = list()
res_emp_cont = list()
res_vol_cont = list()
res_tot_cont = list()
res_vol_perc = list()
res_leverage_people = list()
res_leverage_patches = list()
emails = list()

time_pins = {}

def get_month_key(timestamp):
    d = date.fromtimestamp(timestamp)
    return (d.year, d.month)

def count_contribs(time_key):
    authors = list()
    commits = list()
    for repo_str in repos:
        repo = Repository(repo_str)
        last = repo[repo.head.target]
        employee_authors = set()
        volunteer_authors = set()
        emp_contributions = 0
        vol_contributions = 0
        for commit in repo.walk(last.id, GIT_SORT_TIME):
            tpin = get_month_key(commit.commit_time)
            if tpin != time_key:
                continue;
            authors.append(commit.author)
            commits.append(commit)
            # All entries in authors.keys and emails should be unique at this
            # point.
            author = commit.author
            if (author.email in employees) or ('@mozilla.' in author.email):
                employee_authors.add(author.email)
                emp_contributions += 1
            else:
                volunteer_authors.add(author.email)
                vol_contributions += 1

        res_emp.append(len(employee_authors))
        res_vol.append(len(volunteer_authors))
        res_tot.append(len(employee_authors) + len(volunteer_authors))
        res_emp_cont.append(emp_contributions)
        res_vol_cont.append(vol_contributions)
        res_tot_cont.append(emp_contributions + vol_contributions)
        if not 0 in (emp_contributions, employee_authors, vol_contributions):
            res_vol_perc.append(100 * vol_contributions
                                / (emp_contributions + vol_contributions))
            res_leverage_people.append(float(len(volunteer_authors))
                                       / float(len(employee_authors)))
            res_leverage_patches.append(float(vol_contributions)
                                        / float(len(employee_authors)))

time_keys = []
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    d = datetime.date(year, month, 1)
    return (d.year, d.month)

now = date.fromtimestamp(time.time())
for i in xrange(num_months):
    dym = add_months(now, -i)
    print i
    count_contribs(dym)


print 'employees: ' + str(res_emp) + ','
print 'volunteers: ' + str(res_vol) + ','
print 'total: ' + str(res_tot) + ','
print 'employee_commits: ' + str(res_emp_cont) + ','
print 'volunteer_commits: ' + str(res_vol_cont) + ','
print 'total_commits: ' + str(res_tot_cont) + ','
print 'volunteer_commit_percentage: ' + str(res_vol_perc) + ','
print 'leverage_people: ' + str(res_leverage_people) + ','
print 'leverage_patches: ' + str(res_leverage_patches)


