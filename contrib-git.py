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
repo_summary = dict()

try:
    with open(sys.argv[1]) as r:
        repos = r.read().splitlines()
except:
    print ('Could not read or interpret %s' % sys.argv[1])
    exit -1

employees = list()

try:
    with open(sys.argv[2]) as e:
        employees = e.read().splitlines()
except:
    print ('Could not read or interpret %s' % sys.argv[2])
    exit -1
try:
    num_months = int(sys.argv[3])
except:
    print "That last thing has to be a positive integer."
    exit -1

def get_month_key(timestamp):
    d = date.fromtimestamp(timestamp)
    return (d.year, d.month)

def count_contribs(repo_str,num_months):
    repo = Repository((repo_str).strip())
    last = repo[repo.head.target]
    now = date.fromtimestamp(time.time())
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
    authors = list()
    commits = list()
    for i in xrange(num_months):
        time_key = add_months(i, now)
        print time_key
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
            if (author.email in employees) or "@mozilla." in author.email:
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

    print 'done: ' + repo_str
    print 'employees: ' + str(res_emp) 
    print  'volunteers: ' + str(res_vol)

    filename = "HTML_OUTPUT/" + (repo_str).strip() + '.html' 
    html= open(filename, 'w')

    html.write( '''<!doctype html>
<html>
<head>
<title>Are We Everyone Yet?</title>
<link href="index.css" rel="stylesheet" type="text/css">
</head>
<body>
<script src="./src/Chart.js"></script>
<div class="section header">
<div id="banner">
Are We Everyone Yet?</div>
</div>
<div class="projects"><center>
''')

    for p in repos:
        html.write( '''<a href="%s.html">%s</a> ''' % (p.strip(), p.strip() ))

    html.write('''
</center></div>
<div class="section">
    <center>
    <p><span id="blue">Total</span>, <span id="yellow">Employees</span>, and <span id="red">Volunteer</span> contributors per Firefox release.</p><br/>
    <span id="slogan">Active contributors and employees per release.</span><br/>
    <p><canvas id="contribChart" width="800" height="400"></canvas></p><br/>
    <br/>
    <span id="slogan">Patches from volunteer contributors and employees per release.</span><br/>
    <p><canvas id="contribPercent" width="800" height="400"></canvas></p><br/>
    <span id="slogan">Leverage: Contributers Per Employee</span><br/>
    <p><canvas id="leveragePeopleOverall" width="800" height="400"></canvas></p>
    <span id="slogan">Leverage: Contributor Patches Per Employee</span><br/>
    <p><canvas id="leveragePatchesOverall" width="800" height="400"></canvas></p>
    <span id="slogan">Volunteer Commit Percentage Overall</span><br/>
    <p><canvas id="contribPercentOverall" width="800" height="400"></canvas></p>
</center>
<script>


var myColor = {
        red : "rgba(230, 118, 39 , 1)",
        yellow : "rgba(255, 230, 17 , 1)",
        blue : "rgba(4,174,225, 1)", 
        green : "rgba(57, 181, 17 , 1)"
    } 

   
    document.getElementById("blue").style.color=myColor.blue
    document.getElementById("yellow").style.color=myColor.yellow
    document.getElementById("red").style.color=myColor.red
    
    var participation_data = { 
''' ) 
    html.write('versions: ' + str(list(range( 0 - num_months, 0))) + ',\n' + \
                'employees: ' + str(res_emp) + ',\n' + \
                'volunteers: ' + str(res_vol) + ',\n' + \
                'total: ' + str(res_tot) + ',\n' + \
                'employee_commits: ' + str(res_emp_cont) + ',\n' + \
                'volunteer_commits: ' + str(res_vol_cont) + ',\n' + \
                'total_commits: ' + str(res_tot_cont) + ',\n' + \
                'volunteer_commit_percentage: ' + str(res_vol_perc) + ',\n' + \
                'leverage_people: ' + str(res_leverage_people) + ',\n' + \
                'leverage_patches: ' + str(res_leverage_patches)  )
    html.write( '''
} 
// Volunteers, up first.

var lineGraphData = {
        labels : participation_data.versions,
        datasets : [
                {
        fillColor : "rgba(0,0,0,0)",// : "rgba(0,0,0,0)", //myColor.blue,
        strokeColor :myColor.blue,
        pointColor :myColor.blue,
                        pointStrokeColor : "#fff",
                        data : participation_data.total
                },
                {
        fillColor : "rgba(0,0,0,0)",// :"rgba(0,0,0,0)", //myColor.yellow,
      strokeColor :  myColor.yellow,
      pointColor :  myColor.yellow,
                        pointStrokeColor : "#fff",
                        data : participation_data.employees
                },
                {
        fillColor : "rgba(0,0,0,0)",// : "rgba(0,0,0,0)", //gmyColor.red,
      strokeColor : myColor.red,
      pointColor : myColor.red,
                        pointStrokeColor : "#fff",
                        data : participation_data.volunteers
  }
  ]     
}

var lineGraphParams = { scaleOverride: true, scaleSteps: 15, scaleStepWidth: 40, scaleStepStart: 0, scaleBeginAtZero: true } 

var lineGraph  = new Chart(document.getElementById("contribChart").getContext("2d")).Line(lineGraphData, lineGraphParams);

// Next up, contributor commits.

var commitGraphData = {
        labels : participation_data.versions,
        datasets : [
                {
        fillColor : "rgba(0,0,0,0)",// : myColor.blue,
        strokeColor : myColor.blue,
        pointColor : myColor.blue,
                        pointStrokeColor : "#fff",
                        data : participation_data.total_commits
                },
                {
        fillColor : "rgba(0,0,0,0)",// : myColor.yellow,
        strokeColor : myColor.yellow,
        pointColor : myColor.yellow,
                        pointStrokeColor : "#fff",
                        data : participation_data.employee_commits
                },
                {
        fillColor : "rgba(0,0,0,0)",// : myColor.red,
        strokeColor : myColor.red,
        pointColor : myColor.red,
                        pointStrokeColor : "#fff",
                        data : participation_data.volunteer_commits
  }
  ]     
}

var commitGraphParams = { scaleOverride: true, scaleSteps: 20 , scaleStepWidth: 400, scaleStepsStart: 0, scaleBeginAtZero: true} 

var commitGraph = new Chart(document.getElementById("contribPercent").getContext("2d")).Line(commitGraphData, commitGraphParams);



var percentGraphData = {
        labels : participation_data.versions,
        datasets : [
                {
        fillColor : "rgba(0,0,0,0)",// : myColor.blue, 
        strokeColor : myColor.blue,
        pointColor : myColor.blue,
                        pointStrokeColor : "#fff",
                        data : participation_data.volunteer_commit_percentage
  }
  ]     
}

var percentGraphParams = { scaleOverride: true, scaleSteps: 10 , scaleStepWidth: 10, scaleStepsStart: 0, scaleBeginAtZero: true} 

var percentGraph  = new Chart(document.getElementById("contribPercentOverall").getContext("2d")).Line(percentGraphData, percentGraphParams);

var leveragePeopleGraphData= {
        labels : participation_data.versions,
        datasets : [
                {
        fillColor : "rgba(0,0,0,0)",// : myColor.blue, 
        strokeColor : myColor.blue,
        pointColor : myColor.blue,
                        pointStrokeColor : "#fff",
                        data : participation_data.leverage_people
  }
  ]     
}

var leveragePeopleGraphParams = { scaleOverride: true, scaleSteps: 10 , scaleStepWidth: 0.2, scaleStepsStart: 0, scaleBeginAtZero: true} 

var leveragePeopleGraph= new Chart(document.getElementById("leveragePeopleOverall").getContext("2d")).Line(leveragePeopleGraphData, leveragePeopleGraphParams);

var leveragePatchesGraphData = {
        labels : participation_data.versions,
        datasets : [
                {
        fillColor : "rgba(0,0,0,0)",// : myColor.blue, 
        strokeColor : myColor.blue,
        pointColor : myColor.blue,
                        pointStrokeColor : "#fff",
                        data : participation_data.leverage_patches
  }
  ]     
}

var leveragePatchesGraphParams = { scaleOverride: true, scaleSteps: 10 , scaleStepWidth: 2 , scaleStepsStart: 0, scaleBeginAtZero: true} 

var leveragePatchesGraph  = new Chart(document.getElementById("leveragePatchesOverall").getContext("2d")).Line(leveragePatchesGraphData, leveragePatchesGraphParams);


</script>

</div>
</body>
</html> ''' )

time_keys = []
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    d = datetime.date(year, month, 1)
    return (d.year, d.month)

now = date.fromtimestamp(time.time())
    
for r in repos: 
    count_contribs(r,num_months)



