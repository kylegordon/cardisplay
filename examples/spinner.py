#!/usr/bin/env python
# vim:fileencoding=utf8
# Both python and vim understand the above encoding declaration
# If viewing this on the web, ensure you are viewing with UTF-8 character encoding

import os, sys, time

spinner="|/-\\"
#spinner=".o0O0o. "
#spinner="â‡â‡–â‡‘â‡—â‡’â‡˜â‡“â‡™" #utf8
#spinner="â—“â—‘â—’â—" #utf8
#spinner="â—‹â—”â—‘â—•â—" #utf8
#spinner="â—´â—·â—¶â—µ" #utf8
# Note the following 2 look fine with misc fixed font,
# but under bitstream vera mono at least the characters
# vary between single and double width?
#spinner="â–â–Žâ–â–Œâ–‹â–Šâ–‰â–ˆâ–‰â–Šâ–Œâ–â–Ž" #utf8
#spinner="â–â–‚â–ƒâ–„â–…â–†â–‡â–ˆâ–‡â–†â–…â–„â–ƒâ–‚" #utf8

#convert the utf8 spinner string to a list
chars=[c.encode("utf-8") for c in unicode(spinner,"utf-8")]

def spin():
    pos=0
    while 1:
        sys.stdout.write("\r"+chars[pos])
        sys.stdout.flush()
        time.sleep(.15)
        pos+=1
        pos%=len(chars)

def cursor_visible():
    if os.uname()[0].lower()=="linux":
        os.system("tput cvvis")
def cursor_invisible():
    if os.uname()[0].lower()=="linux":
        os.system("tput civis")

# exit cleanly on Ctrl-C,
# while treating other exceptions as before.
def clean_exit():
    cursor_visible()
    sys.stdout.write("\n")
def cli_exception(type, value, tb):
    if not issubclass(type, KeyboardInterrupt):
        sys.__excepthook__(type, value, tb)
    else:
        clean_exit()
if sys.stdin.isatty():
    sys.excepthook=cli_exception

if __name__ == '__main__':
    cursor_invisible()
    spin()
    clean_exit()

