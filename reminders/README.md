Inspired with 
* https://github.com/mlgill/alfred-workflow-create-reminder, http://www.alfredforum.com/topic/402-create-reminder-in-remindersapp-from-alfred/
* http://www.alfredforum.com/topic/917-reminders/
* http://www.alfredforum.com/topic/2416-reminders-11-a-light-version/?hl=reminders

## Bugs
* "eof" text in notification after reminder creation. That happens only if reminder really created (right list name)
* prints "Created", even if no list exists. Should check, if list exists
* Default list is "Personal". Should allow to specify custom default list.  
http://www.alfredforum.com/topic/307-workflows-best-practices/  
For example type "r --default-list", and select from autocomplete default list (current default should be colored)
Should save it to alfred workflow settings xml file
* Click by notification should go to reminders app
* Cant set "hello \r\n" text. They stripped
* Help text while typing with list of parameters.

## Usage
    
    r Watch Footbal
    # reminder "Watch Footbal" in 10 minutes after now in "Personal" list

    r Watch Football -l Shared List
    # reminder "Watch Football" in list "Shared list"    

    r Watch Football -n Spain vs Germany
    # reminder "Watch Football" with note "Spain vs Germany" in "Personal" list    

    r Watch Footbal -a 20
    # reminder "Watch Footbal" in 20 minutes after now in "Personal" list    

    r Watch Footbal -a 20m
    # same as before
    # reminder "Watch Footbal" in 20 minutes after now in "Personal" list

    r Watch Footbal -a 10h
    # reminder "Watch Footbal" in 10 hours after now in "Personal" list

    r Watch Footbal -a 1d
    # reminder "Watch Footbal" in 1 day after now in "Personal" list

    r Watch Footbal -a 1d10h2m
    # reminder "Watch Footbal" in 1 day, 10 hours and 2 minutes after now in "Personal" list

    r Watch Football -d 10
    # reminder "Watch Football" on first 10th day after today on current time in "Personal" list
    # if today is 10th, then reminder would be created for today

    r Watch Football -d 10/7
    # reminder "Watch Football" on first 10th July after today on current time in "Personal" list
    # if today is 10/7, then reminder would be created for today

    r Watch Football -d 10/7/2013
    # reminder "Watch Football" on 10th July, 2013 year on current time in "Personal" list

    r Watch Football -d tomorrow
    r Watch Football -d tom
    # reminder "Watch Football" on tomorrow on current time in "Personal" list

    r Watch Football -d friday
    # reminder "Watch Football" next friday on current time in "Personal" list
    # if today is Friday, then reminder would be created for today
    Could be used:
        - monday or mon
        - tuesday or tue
        - wednesday or wed
        - thursday or thu
        - friday or fri
        - saturday or sat
        - sunday or sun

    r Watch Football -t 22
    # reminder "Watch Football" today on 22:00 in "Personal" list

    r Watch Football -t 22:45
    # reminder "Watch Football" today on 22:45 in "Personal" list

    r Watch Football -t 10:20am
    # reminder "Watch Football" today on 10:20am in "Personal" list

    r Watch Football -t 10:20pm
    # reminder "Watch Football" today on 10:20pm in "Personal" list

    r Watch Football -d 10/7/2013 -t 22:45
    # reminder "Watch Football" on 10th July, 2013 year on 22:45 in "Personal" list

    r Watch Football -n Spain vs Germany -l Sports -d friday -t 10:45pm
    # reminder "Watch Football" with note "Spain vs Germany" 
    # on next friday on 10:45pm in "Sports" list

Case for words like "tomorrow" or "monday" is not sensitive. "TomorRrow" is same as "tomorrow".  
Position of parameters is no matter. Next examples are equals:
    
    r Watch Football -l Sports -d friday
    r Watch Football -d friday -l Sports

If there is no such date like 31/01/2014, then you'll see error notification:
    
    r Watch Football -d 31/01/2014

    # todo: show notification error
    # todo: show console error

More explicit parameter name could be used with '--' prefix.  
Next examples are equals:

    r Watch Football -n Spain vs Germany
    r Watch Football --note Spain vs Germany

Full set of params:
* -l, --list
* -n, --note
* -a, --after
* -d, --date
* -t, --time