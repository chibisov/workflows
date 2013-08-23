# -*- coding: utf-8 -*-
import datetime
import unittest
from mock import Mock
from unittest import TestCase
import datetime
from StringIO import StringIO

from reminders import Main, ReminderBackendBase, ReminderBackend


def force_str(value):
    if value:
        try:
            return value.encode('utf-8')
        except AttributeError:
            return value
    else:
        return value


class TestReminderBackend(ReminderBackendBase):
    def __init__(self, *args, **kwargs):
        super(TestReminderBackend, self).__init__(*args, **kwargs)
        self._storage = []

    def create(self, **kwargs):
        self._storage.append(kwargs)


class TestMainGetKwargs(TestCase):
    def setUp(self):
        self.datetime_mock = Mock(wraps=datetime)
        self.reminder_backend = TestReminderBackend()
        self.stdout = StringIO()
        self.instance = Main(
            datetime=self.datetime_mock, 
            reminder_backend=self.reminder_backend,
            stdout=self.stdout,
        )        

    def assertExperiments(self, experiments, kwarg_key, kwarg_name):
        for exp in experiments:
            response = self.instance.get_kwargs(args_string=exp['args_string'])
            msg_expected = exp['expected']
            msg_response = response[kwarg_key]
            msg = ('For args_string=="{args_string}" should be used '
                   '{kwarg_name} "{expected}", '
                   'but used "{response}"').format(
                args_string=force_str(exp['args_string']),
                kwarg_name=kwarg_name,
                expected=force_str(msg_expected),
                response=force_str(msg_response),
            )
            self.assertEqual(response[kwarg_key], exp['expected'], msg=msg)

    def test_text(self):
        experiments = [
            {
                'args_string': u'',
                'expected': u'',
            },        
            {
                'args_string': u'   ',
                'expected': u'',
            },                    
            {
                'args_string': u'Watch Football',
                'expected': u'Watch Football',
            },
            {
                'args_string': u'   Watch Football  ',
                'expected': u'Watch Football',
            },
            {
                'args_string': u'Посмотреть футбол',
                'expected': u'Посмотреть футбол',
            },            
        ]
        self.assertExperiments(experiments=experiments, kwarg_key='text', kwarg_name='text')

    def test_list_name(self):
        experiments = [
            {
                'args_string': u'Watch Football',
                'expected': None,
            },
            {
                'args_string': u'Watch Football -l Personal',
                'expected': u'Personal',
            },            
            {
                'args_string': u'Watch Football -l   Мой персональный лист  ',
                'expected': u'Мой персональный лист',
            },
            {
                'args_string': u'Watch Football --list Personal',
                'expected': u'Personal',
            },
        ]
        self.assertExperiments(experiments=experiments, kwarg_key='list', kwarg_name='list name')

    def test_note(self):
        experiments = [
            {
                'args_string': u'Watch Football',
                'expected': None,
            },
            {
                'args_string': u'Watch Football -n Spain vs Germany',
                'expected': u'Spain vs Germany',
            },
            {
                'args_string': u'Watch Football -n Не смотреть сборную России',
                'expected': u'Не смотреть сборную России',
            },            
        ]
        self.assertExperiments(experiments=experiments, kwarg_key='note', kwarg_name='note')

    def test_after(self):
        experiments = [
            {
                'args_string': u'Watch Football -a 10',
                'expected': datetime.timedelta(minutes=10),
            },
            {
                'args_string': u'Watch Football -a 10m',
                'expected': datetime.timedelta(minutes=10),
            },            
            {
                'args_string': u'Watch Football -a 2h',
                'expected': datetime.timedelta(hours=2),
            },
            {
                'args_string': u'Watch Football -a 1d',
                'expected': datetime.timedelta(days=1),
            },
            {
                'args_string': u'Watch Football -a 1d2h10m',
                'expected': datetime.timedelta(days=1, hours=2, minutes=10),
            },
            {
                'args_string': u'Watch Football -a 100m20h10d',
                'expected': datetime.timedelta(days=10, hours=20, minutes=100),
            },
            {
                'args_string': u'Watch Football --after 100m20h10d',
                'expected': datetime.timedelta(days=10, hours=20, minutes=100),
            },            
        ]
        self.assertExperiments(experiments=experiments, kwarg_key='after', kwarg_name='timedelta')

    def test_date(self):
        self.datetime_mock.date.today = Mock(return_value=datetime.date(year=1990, month=3, day=2))
        experiments = [
            # only day
            {
                'args_string': 'Watch Football -d 10',
                'expected': datetime.date(day=10, month=3, year=1990),
            },
            {
                'args_string': 'Watch Football -d 2',
                'expected': datetime.date(day=2, month=3, year=1990),
            },
            {
                'args_string': 'Watch Football -d 1',
                'expected': datetime.date(day=1, month=4, year=1990),
            },
            {
                'args_string': 'Watch Football -d 01',
                'expected': datetime.date(day=1, month=4, year=1990),
            },
            {
                'args_string': 'Watch Football -d 01/',
                'expected': datetime.date(day=1, month=4, year=1990),
            },            
            # only day and month
            {
                'args_string': 'Watch Football -d 2/3',
                'expected': datetime.date(day=2, month=3, year=1990),
            },            
            {
                'args_string': 'Watch Football -d 10/5',
                'expected': datetime.date(day=10, month=5, year=1990),
            },
            {
                'args_string': 'Watch Football -d 10/05',
                'expected': datetime.date(day=10, month=5, year=1990),
            },            
            {
                'args_string': 'Watch Football -d 10/05/',
                'expected': datetime.date(day=10, month=5, year=1990),
            },
            {
                'args_string': 'Watch Football -d 1/3/',
                'expected': datetime.date(day=1, month=3, year=1991),
            }, 
            # day, month and year
            {
                'args_string': 'Watch Football -d 1/2/1890',
                'expected': datetime.date(day=1, month=2, year=1890),
            },
            {
                'args_string': 'Watch Football -d 1/2/1890/',
                'expected': datetime.date(day=1, month=2, year=1890),
            },            
        ]
        self.assertExperiments(experiments=experiments, kwarg_key='date', kwarg_name='date')

    def test_date__day_of_next_year(self):
        self.datetime_mock.date.today = Mock(return_value=datetime.date(year=1990, month=12, day=28))
        experiments = [
            {
                'args_string': 'Watch Football -d 29',
                'expected': datetime.date(year=1990, month=12, day=29),
            },
            {
                'args_string': 'Watch Football -d 10',
                'expected': datetime.date(year=1991, month=1, day=10),
            },
        ]
        self.assertExperiments(experiments=experiments, kwarg_key='date', kwarg_name='date')    

    def test_date_from_human_text(self):
        # 2/3/1990 was a Monday
        self.datetime_mock.date.today = Mock(return_value=datetime.date(year=1990, month=3, day=5))
        experiments = [
            # tomorrow
            {
                'args_string': 'Watch Football -d tomorrow',
                'expected': datetime.date(year=1990, month=3, day=6),
            },
            {
                'args_string': 'Watch Football -d tom',
                'expected': datetime.date(year=1990, month=3, day=6),
            },
            {
                'args_string': 'Watch Football -d   tom  ',
                'expected': datetime.date(year=1990, month=3, day=6),
            },            
            {
                'args_string': 'Watch Football -d TomoRrow',
                'expected': datetime.date(year=1990, month=3, day=6),
            }, 
            # monday (today)
            {
                'args_string': 'Watch Football -d monday',
                'expected': datetime.date(year=1990, month=3, day=5),
            },
            {
                'args_string': 'Watch Football -d mon',
                'expected': datetime.date(year=1990, month=3, day=5),
            },
            # tuesday
            {
                'args_string': 'Watch Football -d tuesday',
                'expected': datetime.date(year=1990, month=3, day=6),
            },
            {
                'args_string': 'Watch Football -d tue',
                'expected': datetime.date(year=1990, month=3, day=6),
            },
            # wednesday
            {
                'args_string': 'Watch Football -d wednesday',
                'expected': datetime.date(year=1990, month=3, day=7),
            },
            {
                'args_string': 'Watch Football -d wed',
                'expected': datetime.date(year=1990, month=3, day=7),
            },
            # thursday
            {
                'args_string': 'Watch Football -d thursday',
                'expected': datetime.date(year=1990, month=3, day=8),
            },
            {
                'args_string': 'Watch Football -d thu',
                'expected': datetime.date(year=1990, month=3, day=8),
            },
            # friday
            {
                'args_string': 'Watch Football -d friday',
                'expected': datetime.date(year=1990, month=3, day=9),
            },
            {
                'args_string': 'Watch Football -d fri',
                'expected': datetime.date(year=1990, month=3, day=9),
            },
            # saturday
            {
                'args_string': 'Watch Football -d saturday',
                'expected': datetime.date(year=1990, month=3, day=10),
            },
            {
                'args_string': 'Watch Football -d sat',
                'expected': datetime.date(year=1990, month=3, day=10),
            },
            # sunday
            {
                'args_string': 'Watch Football -d sunday',
                'expected': datetime.date(year=1990, month=3, day=11),
            },
            {
                'args_string': 'Watch Football -d sun',
                'expected': datetime.date(year=1990, month=3, day=11),
            },            
        ]        
        self.assertExperiments(experiments=experiments, kwarg_key='date', kwarg_name='date')

    def test_time(self):
        experiments = [        
            {
                'args_string': 'Watch Football',
                'expected': None,
            },        
            {
                'args_string': 'Watch Football -t 10',
                'expected': datetime.time(hour=10),
            },
            {
                'args_string': 'Watch Football -t 22',
                'expected': datetime.time(hour=22),
            },            
            {
                'args_string': 'Watch Football -t 10am',
                'expected': datetime.time(hour=10),
            },            
            {
                'args_string': 'Watch Football -t 10pm',
                'expected': datetime.time(hour=22),
            },
            {
                'args_string': 'Watch Football -t 10:30',
                'expected': datetime.time(hour=10, minute=30),
            },
            {
                'args_string': 'Watch Football -t 10:30am',
                'expected': datetime.time(hour=10, minute=30),
            },
            {
                'args_string': 'Watch Football -t 10:30pm',
                'expected': datetime.time(hour=22, minute=30),
            },
            {
                'args_string': 'Watch Football -t 1',
                'expected': datetime.time(hour=1),
            },            
            {
                'args_string': 'Watch Football -t 1pm',
                'expected': datetime.time(hour=13),
            },
            {
                'args_string': 'Watch Football -t 1:15pm',
                'expected': datetime.time(hour=13, minute=15),
            },
        ]
        self.assertExperiments(experiments=experiments, kwarg_key='time', kwarg_name='time')


class TestMainGetKwargsForReminderBackend(TestCase):
    def setUp(self):
        self.datetime_mock = Mock(wraps=datetime)
        self.reminder_backend = TestReminderBackend()
        self.stdout = StringIO()
        self.instance = Main(
            datetime=self.datetime_mock, 
            reminder_backend=self.reminder_backend,
            stdout=self.stdout,
        )

    def assertExperiments(self, experiments):
        for exp in experiments:
            response = self.instance.get_kwargs_for_reminder_backend(exp['kwargs'])
            self.assertEqual(response, exp['expected'])

    def test_experiments(self):
        self.datetime_mock.date.today = Mock(return_value=datetime.date(year=1990, month=3, day=5))
        self.datetime_mock.datetime.now = Mock(return_value=datetime.datetime(year=1990, month=3, day=5))
        default_date_time = self.datetime_mock.datetime.now() + self.datetime_mock.timedelta(minutes=10)
        experiments = [
            # only text
            {
                'kwargs': {
                    'text': 'Watch Football',
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': default_date_time
                }
            },  
            # text and after  
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'after': self.datetime_mock.timedelta(minutes=100)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': self.datetime_mock.datetime.now() + self.datetime_mock.timedelta(minutes=100)
                }
            }, 
            # text and date  
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'date': self.datetime_mock.date(day=10, month=12, year=1990)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': self.datetime_mock.datetime(day=10, month=12, year=1990)
                }
            },            
            # text and time  
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'time': self.datetime_mock.time(hour=10, minute=22)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': self.datetime_mock.datetime.combine(
                        self.datetime_mock.date.today(), 
                        self.datetime_mock.time(hour=10, minute=22)
                    )
                }
            },
            # text, date and time 
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'date': self.datetime_mock.date(day=10, month=12, year=1990),
                    'time': self.datetime_mock.time(hour=10, minute=22)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': self.datetime_mock.datetime(day=10, month=12, year=1990, hour=10, minute=22)
                }
            },
            # text and list
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'list': u'Личный'
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': u'Личный',
                    'note': None,
                    'date_time': default_date_time
                }
            },
            # text and note
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'note': u'Не смотреть сборную России'
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': u'Не смотреть сборную России',
                    'date_time': default_date_time
                }
            },            
            # text, list, note, date and time
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'list': 'Personal',
                    'note': u'Не смотреть сборную России',
                    'date': self.datetime_mock.date.today(),
                    'time': self.datetime_mock.time(hour=22)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': u'Не смотреть сборную России',
                    'date_time': self.datetime_mock.datetime.combine(
                        self.datetime_mock.date.today(), 
                        self.datetime_mock.time(hour=22)
                    )
                }
            }
        ]
        self.assertExperiments(experiments)

    def test_date_time_and_after(self):
        "After should be used as a last resort"
        self.datetime_mock.date.today = Mock(return_value=datetime.date(year=1990, month=3, day=5))
        self.datetime_mock.datetime.now = Mock(return_value=datetime.datetime(year=1990, month=3, day=5))
        experiments = [        
            # text, date and after 
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'date': self.datetime_mock.date(day=10, month=12, year=1990),
                    'after': self.datetime_mock.timedelta(minutes=1)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': self.datetime_mock.datetime(day=10, month=12, year=1990)
                }
            },     
            # text, time and after 
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'time': self.datetime_mock.time(hour=10, minute=22),
                    'after': self.datetime_mock.timedelta(minutes=1)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': self.datetime_mock.datetime.combine(
                        self.datetime_mock.date.today(), 
                        self.datetime_mock.time(hour=10, minute=22)
                    )
                }
            },
            # text, date, time and after 
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'date': self.datetime_mock.date(day=10, month=12, year=1990),
                    'time': self.datetime_mock.time(hour=10, minute=22),
                    'after': self.datetime_mock.timedelta(minutes=1)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': self.datetime_mock.datetime(day=10, month=12, year=1990, hour=10, minute=22)
                }
            },
            # text and after
            {
                'kwargs': {
                    'text': 'Watch Football',
                    'after': self.datetime_mock.timedelta(minutes=1)
                },
                'expected': {
                    'text': 'Watch Football',
                    'list_name': 'Personal',
                    'note': None,
                    'date_time': self.datetime_mock.datetime.now() + self.datetime_mock.timedelta(minutes=1)
                }
            },
        ]  
        self.assertExperiments(experiments)   


class TestMainRun(TestCase):
    def setUp(self):
        self.datetime_mock = Mock(wraps=datetime)
        self.reminder_backend = TestReminderBackend()
        self.stdout = StringIO()
        self.instance = Main(
            datetime=self.datetime_mock, 
            reminder_backend=self.reminder_backend,
            stdout=self.stdout,
        )
        self.backend_kwargs = {
            'text': u'Посмотреть Футбол',
            'list_name': 'Personal',
            'note': 'Spain vs Germany',
            'date_time': self.datetime_mock.datetime.now()
        }
        self.instance.get_kwargs_for_reminder_backend = Mock(return_value=self.backend_kwargs)

    def test_should_run_backend_create_process(self):
        self.instance.run(u'Посмотреть Футбол')
        self.assertEqual(len(self.instance.reminder_backend._storage), 1)
        self.assertEqual(self.instance.reminder_backend._storage[0], self.backend_kwargs)

    def test_should_write_to_stdout_success_text(self):
        self.instance.run(u'Посмотреть Футбол')
        self.assertEqual(self.instance.stdout.getvalue(), u'Created reminder: Посмотреть Футбол\n'.encode('utf-8'))


if __name__ == '__main__':
    unittest.main()