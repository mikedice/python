import time

"""
Python countdown timer. Counts down minutes and seconds
using time.sleep in a loop. Note that this is probably not
the best precision timer but it is good for demonstration
purposes.


"""

# the settings values are input to this program in some way
# that is left as an excercise for the reader
secondsSetting = 0
minutesSetting = 3

# make copies of the settings which we can update below
seconds = secondsSetting
minutes = minutesSetting

# the program loop - prints the countdown timer  formatted in minutes
# and seconds
while True:
    print '{:0>2d}:{:0>2d}'.format(minutes, seconds )

    # Count down seconds and then check if we've counted
    # down below 0 seconds. If we did then count down
    # the minutes and check to see if we timed out
    seconds=seconds-1
    if seconds < 0:
        minutes = minutes-1
        if minutes < 0:
            print('timed out')
            break
        else:
            seconds = 59

    # sleep for one seconds using time.sleep
    # Note that this is probably not the highest precision
    # way to count seconds but should be a good approximation
    time.sleep(1.0)

