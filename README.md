## About
Set of usefull alfred workflows. Alfa release.
The main difference from other workflows, that these could be used from console without alfred at all.  
For example in alfred you could create reminder like this:

    r Watch Football -d tomorrow

And you can use console for the same action:

    python reminders.py Watch Football -d tomorrow

And there is no magic in parameters parsing. You just use standart console arguments like -d or --date.  
Python standart library is used. You don't need to install additional packages from pip (except for running tests)

## Workflows
[Reminders.app workflow](Reminders.app workflow)
    
    r Watch Football -d tomorrow

## Running tests
Firstly install requirements

    $ pip install -r test_requirements.txt

Then just run one of the test files:

    $ python reminders/src/tests.py