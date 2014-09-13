    #!/usr/bin/python
# -*- coding: UTF-8 -*-

from Module import Module

class F1(Module):
    def __init__(self, parent):
        Module.__init__(self, parent, 'f1', '!f1')
        return

    def get_json(self, url, table):
        import commands, json, sys
        reload(sys)
        sys.setdefaultencoding("utf8")

        self.log('about to fetch: ' + url)
        json_data = unicode(commands.getstatusoutput('curl --silent -L --insecure -A "Mozilla/4.73 [en] (X11; U; Linux 2.2.15 i686)" "%s"' % url)[1])
        data = json.loads(json_data)
        if not data:
            return None
        return data['MRData'][table]

    def get_drivers(self):
        url = 'http://ergast.com/api/f1/current/driverStandings.json'
        race = self.get_json(url, 'StandingsTable')
        if not race:
            return
        year = self.year(race)

        row_format = "{0:>1}{1:>8}{2:>20}{3:>14}{4:>8}{5:>8}"
        columns = ['Position', 'Driver', 'Constructor', 'Points', 'Wins']
        results = [year + ' Driver Standings (more: http://ergast.com/api/f1/current/driverStandings)']
        results += [row_format.format("", *columns)]
        i = 0
        for d in race['StandingsLists'][0]['DriverStandings']:
            to_format = [
                self.position(d),
                u' '.join([self.given_name(d), self.family_name(d)]),
                self.constructors(d),
                self.points(d),
                self.wins(d)
            ]
            results += [row_format.format("", *to_format)]
        return '\n'.join(results)

    def get_constructors(self):
        url = 'http://ergast.com/api/f1/current/constructorStandings.json'
        race = self.get_json(url, 'StandingsTable')
        if not race:
            return
        year = self.year(race)

        row_format = "{0:>1}{1:>8}{2:>14}{3:>8}{4:>8}"
        columns = ['Position', 'Constructor', 'Points', 'Wins']
        results = [year + ' Constructor Standings (more: http://ergast.com/api/f1/current/constructorStandings)']
        results += [row_format.format("", *columns)]
        i = 0
        for d in race['StandingsLists'][0]['ConstructorStandings']:
            to_format = [
                self.position(d),
                self.constructor(d),
                self.points(d),
                self.wins(d)
            ]
            results += [row_format.format("", *to_format)]
        return '\n'.join(results)

    def get_qualifying(self):
        url = 'http://ergast.com/api/f1/current/last/qualifying.json'
        race = self.get_json(url, 'RaceTable')
        if not race:
            return
        year = self.year(race)
        raceName = self.raceName(race)

        row_format = "{0:>1}{1:>8}{2:>20}{3:>20}{4:>14}{5:>14}{6:>14}"
        columns = ['Position', 'Driver', 'Constructor', 'Q1', 'Q2', 'Q3']
        results = [u' '.join([year, raceName]) + '  (more: http://ergast.com/api/f1/current/last/qualifying)']
        results += [row_format.format("", *columns)]
        i = 0
        for d in race['Races'][0]['QualifyingResults']:
            to_format = [
                self.position(d),
                u' '.join([self.given_name(d), self.family_name(d)]),
                self.constructor(d),
                self.q1(d),
                self.q2(d),
                self.q3(d)
            ]
            results += [row_format.format("", *to_format)]
        return '\n'.join(results)

    def get_results(self):
        url = 'http://ergast.com/api/f1/current/last/results.json'
        race = self.get_json(url, 'RaceTable')
        if not race:
            return
        year = self.year(race)
        raceName = self.raceName(race)

        row_format = "{0:>1}{1:>8}{2:>20}{3:>8}{4:>8}{5:>14}{6:>12}{7:>8}"
        columns = ['Position', 'Driver', 'Laps', 'Pole', 'Time', 'Status', 'Points']
        results = [u' '.join([year, raceName]) + '\n']
        results += [row_format.format("", *columns) + '\n']
        for d in race['Races'][0]['Results']:
            to_format = [
                self.position(d),
                u' '.join([self.given_name(d), self.family_name(d)]),
                self.laps(d),
                self.grid(d),
                self.time(d),
                self.status(d),
                self.points(d)
            ]
            results += [row_format.format("", *to_format)]
        return '\n'.join(results)

    def constructors(self, d):
        return d['Constructors'][0]['name']
    def constructor(self, d):
        return d['Constructor']['name']
    def q1(self, d):
        if not 'Q1' in d:
            return '-'
        return d['Q1']
    def q2(self, d):
        if not 'Q2' in d:
            return '-'
        return d['Q2']
    def q3(self, d):
        if not 'Q3' in d:
            return '-'
        return d['Q3']
    def position(self, d):
        return d['position']
    def given_name(self, d):
        return d['Driver']['givenName']
    def family_name(self, d):
        return d['Driver']['familyName']
    def laps(self, d):
        return d['laps']
    def grid(self, d):
        return d['grid']
    def time(self, d):
        if not 'Time' in d:
            return "-"
        return d['Time']['time']
    def status(self, d):
        return d['status']
    def points(self, d):
        return d['points']
    def wins(self, d):
        return d['wins']
    def year(self, race):
        return race['season']
    def raceName(self, race):
        return race['Races'][0]['raceName']

    def get_f1(self):
        import commands, json
        from dateutil import tz
        from datetime import datetime

        url = 'http://ergast.com/api/f1/current/next.json'
        race = self.get_json(url, 'RaceTable')
        if not race:
            return

        year = race['season']
        circuit = race['Races'][0]['Circuit']['circuitName']
        raceName = race['Races'][0]['raceName']
        time = race['Races'][0]['time']
        date = race['Races'][0]['date']

        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Europe/Stockholm')

        utc = datetime.strptime("%s %s" % (date, time), '%Y-%m-%d %H:%M:%SZ')
        utc = utc.replace(tzinfo=from_zone)
        local_time = utc.astimezone(to_zone)
        time_to_race = self.time_from_now(local_time, to_zone)
        return "Next race is %s %s, %s at %s %s" % (year, raceName, circuit, local_time, time_to_race)

    def time_from_now(self, local_time, to_zone):
        from datetime import datetime
        now = datetime.now(to_zone)
        if now > local_time:
            return 'already started'
        diff = self.total_seconds(local_time - now)
        days = divmod(diff, 86400)
        hours = divmod(days[1], 3600)
        mins = divmod(hours[1], 60)
        days_str = str(int(days[0])) + ' day%s, '%self.plural(days[0]) if days[0] > 0 else ''
        hours_str = str(int(hours[0])) + ' hour%s, '%self.plural(hours[0]) if hours[0] > 0 else ''
        mins_str = str(int(mins[0])) + ' minute%s'%self.plural(mins[0]) if mins[0] > 0 else 'already started'
        return "(%s%s%s)" % (days_str, hours_str, mins_str)

    def total_seconds(self, td):
        return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

    def plural(self, nr):
        return 's' if nr > 1 else ''

    def get_help(self):
        opts  = "  !f1                     default, shows when and where the next race is\n"
        opts += "  !f1 <drivers|d>         shows the current drivers' standings             (anwers in private message)\n"
        opts += "  !f1 <constructors|c>    shows the current constructors' standings        (anwers in private message)\n"
        opts += "  !f1 <results|r>         shows the results from the last race             (anwers in private message)\n"
        opts += "  !f1 <qualifying|q>      shows the results from the last qualifying       (anwers in private message)\n"
        opts += "  !f1 <help|h>            shows this help\n"
        return opts

    def get_error(self, line):
        return "Unknown command '" + line + "', use '!f1 help' to see available commands."

    # required function
    def process_line(self):
        import sys
        line = self.fifo_pop()
        self.log('getting f1 data')

        retries = 5
        current = 1
        f1data = None

        while current < retries:
          target = self.event.source().split('!')[0]
          try:
            if not line:
                f1data = self.get_f1()
                target = None
            elif line == 'help' or line == 'h':
                f1data = self.get_help()
                target = None
            elif line == 'constructors' or line == 'c':
                f1data = self.get_constructors()
            elif line == 'drivers' or line == 'd':
                f1data = self.get_drivers()
            elif line == 'qualifying' or line == 'q':
                f1data = self.get_qualifying()
            elif line == 'results' or line == 'r':
                f1data = self.get_results()
            else:
                f1data = self.get_error(line)
                target = None
            break
          except:
            print "Unexpected error: ", sys.exc_info()
            self.log('ERROR: could not get f1 data, might retry')
            current+=1
            continue

        if not f1data:
            self.log('ERROR: could not get f1data')
            self.send('Could not get data')
            return

        import time
        f1data = f1data.split('\n')
        i = 0
        for w in f1data:
            if i > 3:
                time.sleep(0.5)
            self.send(w, target)
            i = i + 1
        return

