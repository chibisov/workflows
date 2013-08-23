# -*- coding: utf-8 -*-
import argparse
import shlex
from itertools import chain
from copy import deepcopy
import re
import os
from contextlib import contextmanager


def is_called_from_alfred():
    # todo: test me
    return '{query}' != '{' + 'query' + '}'


@contextmanager
def ignore(*exceptions):
    try:
        yield
    except exceptions:
        pass    


class ReminderBackendBase(object):
    def create(self, text, list_name, date_time, note=None):
        """
        Creates reminder
        """
        raise NotImplementedError()


class ReminderBackend(ReminderBackendBase):
    def create(self, text, list_name, date_time, note=None):
        # todo: alert, if there is not such list
        make_command = self.get_make_command(text, list_name, date_time, note)
        os.system(make_command.encode('utf-8'))

    def get_make_command(self, text, list_name, date_time, note):
        """
        http://hints.macworld.com/article.php?story=20040617170055379
        """
        # todo: test me
        make_command = 'make new reminder with properties {name:"%(text)s", due date:date("%(date_time)s")' % {
            'text': text,
            'date_time': date_time.strftime('%d/%m/%Y %H:%M')
        }
        if note:
            make_command += ', note:%(note)s' % {'note': note}
        else:
            make_command += '}'

        return u"""
        exec osascript <<\EOF
        tell application "Reminders"
            tell list "%(list_name)s"
                %(make_command)s
            end tell
        end tell
        EOF
        """ % {
            'list_name': list_name,
            'make_command': make_command
        }


class Main(object):
    def __init__(self, datetime, reminder_backend, stdout):
        self.datetime = datetime        
        self.reminder_backend = reminder_backend
        self.stdout = stdout

    def get_kwargs(self, args_string):
        parser = self.get_parser()
        text, argv = self.get_argv(args_string, parser)
        kwargs = dict(parser.parse_args(argv)._get_kwargs())
        kwargs['text'] = text
        kwargs = self.post_process_kwargs(deepcopy(kwargs))
        return kwargs

    def get_argv(self, args_string, parser):
        option_strings = list(chain(*[i.option_strings for i in parser._actions]))
        splitted_list = self._get_splitted_list(args_string)       
        final_list = []
        is_first_iter = True
        text = ''
        is_join_to_new = False
        for item in splitted_list:
            if item in option_strings:
                final_list.append(item)
                is_first_iter = False
                is_join_to_new = True
            else:
                if is_first_iter:
                    text += ' ' + item
                    continue
                if is_join_to_new:
                    final_list.append('')
                    is_join_to_new = False
                final_list[-1] += ' ' + item
        final_list = [i.strip() for i in final_list]
        return text.strip(), final_list

    def _get_splitted_list(self, args_string):
        """
        http://stackoverflow.com/questions/14218992/shlex-split-still-not-supporting-unicode
        """
        return [i.decode('utf-8') for i in shlex.split(args_string.encode('utf-8'))]

    def post_process_kwargs(self, kwargs):
        kwargs['after'] = self.post_process_after(kwargs['after'])
        kwargs['date'] = self.post_process_date(kwargs['date'])
        kwargs['time'] = self.post_process_time(kwargs['time'])
        return kwargs

    def post_process_after(self, value):
        if not value:
            return None
        days, hours, minutes = self.get_data_for_timedelta_from_string(value)
        return self.datetime.timedelta(days=days, hours=hours, minutes=minutes)

    def get_data_for_timedelta_from_string(self, value):
        result = {
            'days': 0,
            'hours': 0,
            'minutes': 0
        }
        try:
            result['minutes'] = int(value)
        except ValueError:
            for key in result:
                found = re.search(r'(?P<search>\d+){0}'.format(key[0]), value)
                if found:
                    result[key] = int(found.groupdict().get('search'))
                else:
                    result[key] = 0  
        return result['days'], result['hours'], result['minutes']     

    def post_process_date(self, value):
        if not value:
            return None
        try:
            bits = [int(i) for i in value.split('/') if i]
        except ValueError:
            return self.get_date_from_human_text(value.lower())
        else:
            return self.get_date_from_bits(bits)

    def get_date_from_human_text(self, value):
        if value in [u'tomorrow', u'tom']:
            return self.datetime.date.today() + self.datetime.timedelta(days=1)
        elif value in [u'monday', u'mon']:
            return self.get_next_week_day(0)
        elif value in [u'tuesday', u'tue']:
            return self.get_next_week_day(1)
        elif value in [u'wednesday', u'wed']:
            return self.get_next_week_day(2)
        elif value in [u'thursday', u'thu']:
            return self.get_next_week_day(3)
        elif value in [u'friday', u'fri']:
            return self.get_next_week_day(4)
        elif value in [u'saturday', u'sat']:
            return self.get_next_week_day(5)
        elif value in [u'sunday', u'sun']:
            return self.get_next_week_day(6)

    def get_next_week_day(self, week_day):
        today = self.datetime.date.today()
        today_week_day = today.weekday()
        for day in range(7):
            date = today + self.datetime.timedelta(days=day)
            if date.weekday() == week_day:
                return date

    def get_date_from_bits(self, bits):
        if len(bits) == 1:
            return self.get_next_day_from_today(bits[0])
        elif len(bits) == 2:
            return self.get_next_day_on_next_month_from_today(bits[0], bits[1])
        else:
            return self.datetime.date(day=bits[0], month=bits[1], year=bits[2])        

    def get_next_day_from_today(self, day):
        today = self.datetime.date.today()
        if today.day > day:
            new_month = today.month + 1
            new_year = today.year
            if new_month > 12:
                new_month = 1
                new_year += 1
        else:
            new_month = today.month
            new_year = today.year
        return self.datetime.date(year=new_year, month=new_month, day=day)

    def get_next_day_on_next_month_from_today(self, day, month):
        today = self.datetime.date.today()
        new_year = today.year        
        if today.month >= month:
            if today.day != day:
                new_year += 1
        return self.datetime.date(year=new_year, month=month, day=day)

    def post_process_time(self, value):
        """
        %H  Hour (24-hour clock) as a zero-padded decimal number.   00, 01, ..., 23  
        %I  Hour (12-hour clock) as a zero-padded decimal number.   01, 02, ..., 12
        %M  Minute as a zero-padded decimal number. 00, 01, ..., 59
        %p  Locale's equivalent of either AM or PM. 
            AM, PM (en_US);
            am, pm (de_DE)        
        """
        if not value:
            return None
        try:
            hour = int(value)
        except ValueError:
            with ignore(ValueError):
                return self.datetime.datetime.strptime(value, '%I%p').time()
            with ignore(ValueError):
                return self.datetime.datetime.strptime(value, '%H:%M').time()
            with ignore(ValueError):
                return self.datetime.datetime.strptime(value, '%I:%M%p').time()
        else:
            return self.datetime.time(hour=hour)

    def get_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-n', 
            '--note', 
            help='Reminder note', 
            required=False
        )
        parser.add_argument(
            '-a', 
            '--after', 
            help='Reminder time after', 
            required=False
        )
        parser.add_argument(
            '-d', 
            '--date', 
            help='Reminder date', 
            required=False
        )
        parser.add_argument(
            '-t', 
            '--time', 
            help='Reminder time', 
            required=False
        )        
        parser.add_argument(
            '-l', 
            '--list', 
            help='Reminder list',
            required=False
        )        
        return parser

    def get_kwargs_for_reminder_backend(self, kwargs):
        return self._prepare_kwargs_for_reminder_backend(kwargs)

    def _prepare_kwargs_for_reminder_backend(self, kwargs):
        return {
            'text': kwargs['text'],
            'list_name': kwargs.get('list', 'Personal'),
            'note': kwargs.get('note'),
            'date_time': self._get_datetime_for_reminder_backend(
                after=kwargs.get('after'),
                date=kwargs.get('date'),
                time=kwargs.get('time'),
            )
        }
    
    def _get_datetime_for_reminder_backend(self, after, date, time):
        if date and time:
            return self.datetime.datetime.combine(date, time)
        elif date:
            return self.datetime.datetime.combine(date, self.datetime.time())
        elif time:
            return self.datetime.datetime.combine(self.datetime.date.today(), time)
        elif after:
            return self.datetime.datetime.now() + after
        else:
            return self.datetime.datetime.now() + self.datetime.timedelta(minutes=10)

    def run(self, args_string):
        # todo: wrap with try and print traceback on exception
        kwargs = self.get_kwargs(args_string)
        backend_kwargs = self.get_kwargs_for_reminder_backend(kwargs)
        self.reminder_backend.create(**backend_kwargs)
        success_text = u'Created reminder: ' + backend_kwargs['text'] + '\n'
        success_text = success_text.encode('utf-8')
        self.stdout.write(success_text)


if __name__ == '__main__':
    # todo: test me
    import datetime
    import sys

    if is_called_from_alfred():
        args_string = '{query}'.decode('utf-8')
    else:
        args_string = u' '.join([i.decode('utf-8') for i in sys.argv[1:]])

    Main(
        datetime=datetime, 
        reminder_backend=ReminderBackend(),
        stdout=sys.stdout
    ).run(args_string=args_string)
