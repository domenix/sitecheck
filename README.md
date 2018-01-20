# sitecheck

CLI program for regularly checking a website and send detected changes to provided email addresses.

Change is considered as content change defined by the user; to avoid false alarms because of dynamic html links and ads, the user has to provide a list of keywords, and if the amount of them will change on the website, it will trigger.  
In the first run, it saves the html file to the folder of the script, then regularly compares it with a file containing wordlists, separated by newlines.

For optimal operation, use every word as a separate wordlist altogether, because if two words are in the same wordlist, and one of them appears one more time on the site, but the other word appears one less time, the check will not trigger. As a separate wordlist, they are separately observed, and if change is detected from the inital html file, then the check will trigger.
