import time, getpass, imaplib, smtplib, email, re, sys, uuid
from email.mime.text import MIMEText
from email.parser import FeedParser
from email.message import Message
from email.header import Header

# Loade in UserEmails from file
contact = {}
with open("UserEmails.txt") as e:
	for line in e:
		(key, val) = line.split(", ")
		contact[str(key)] = val[0:-1]

def set_proc_name(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)

def splitSend(msgList, M):
    # Truncate checked emails to the most recent 50
    msgList = msgList.split()
    msgList = msgList[-100:]
    
    # Import Sent List, trim to last 1000 and set as sentlist
    with open("sent.txt") as sentlist:
        sentlist = sentlist.read().split("\n")

    sl = open("sent.txt", "w")
    for i in sentlist[-1000:]:
        sl.write("\n" + i)
    sl.close()

    with open("sent.txt") as sentlist:
        sentlist = sentlist.read().split("\n")
    
    # Import Checked List, trim to last 1000 and set as checked
    with open("checked.txt") as checked:
        checked = checked.read().split("\n")

    cl = open("checked.txt", "w")
    for i in checked[-1000:]:
        cl.write("\n" + i)
    cl.close()

    with open("checked.txt") as checked:
        checked = checked.read().split("\n")
    
    # Set default values for email statuses
    sendemail = False
    sendcomplete = False

    # Remove emails that have already been checked or sent
    for i in checked:
        for a in msgList:
            if i == a:
                msgList.remove(i)
    for i in sentlist:
        for a in msgList:
            if i == a:
                msgList.remove(i)

    # Check remaining emails in msgList
    for num in msgList:
	print ("Checking Message")
        typ, subj = M.uid('fetch', num, '(BODY[HEADER.FIELDS (SUBJECT)])')
        try:
            print ("Checking Subject " + num + ": " + subj[0][1])
            if "[#" in subj[0][1]:
                # Set variables needed if "[#" is in the subject
                typ, fromaddr = M.uid('fetch', num, '(BODY[HEADER.FIELDS (FROM)])')
                typ, header = M.uid('fetch', num, '(BODY[HEADER])')
                typ, body = M.uid('fetch', num, '(BODY[TEXT])')
                typ, cType = M.uid('fetch', num, '(BODY[HEADER.FIELDS (CONTENT-TYPE)])')
                
                sendemail = True
                emailmatch = False
                fromemail = "redmine@myIntranet.intranet" # Default from email if a match is not found
                
                try: # Attempt to match from name to internal email address
                    for key, value in contact.items():
                        if key in fromaddr[0][1]:
                            print ("known address")
                            print (value)
                            fromemail = value
                            emailmatch = True
                            print ("email sent from " + value)
                        else:
                            print "unknown email address"
                except:
                    print ("Contact not in list")

                if "boundary" in cType[0][1]: # Collect email boundary if present
                    boundary = cType[0][1].split('boundary=');
                    if '"' in boundary[-1]:
                        boundary = boundary[-1].split('"')[1]
                    else:
                        boundary = boundary[-1]
                else:
                    boundary = ""
                    
                # Compile message from collected data
                message = (header[0][1] + "\n--" + boundary + "\nExternal Email " + subj[0][1] + "\n" + fromaddr[0][1] + body[0][1])

                try:
                    sendMail(message, fromemail)
                    sendcomplete = True
                except:
                    print ("send email failed")
                if sendcomplete == True: # Update sent list
                    sent = open('sent.txt', 'a')
                    sent.write("\n" + num)
                    sent.close() 
            if sendemail == False or sendcomplete == True: # Update Checked list
                checked = open('checked.txt', 'a')
                checked.write("\n" + num)
                checked.close() 
        except:
            print ("Failed to check subject for " + subj[0][1])
    
def checkMail():
    M = imaplib.IMAP4_SSL("imap.myDomain.com", 993) # Email settings for the external email address to watch
    email = "me@myDomain.com"
    password = "password"
    M.login(email, password)
    M.select("[Gmail]/Sent Mail")
    typ, data = M.uid('search', None, "ALL")

    splitSend(data[0], M)
    M.select("Inbox")
    
    typ, data = M.uid('search', None, "ALL")
    splitSend(data[0], M)
    
    M.close()
    M.logout()

def sendMail(msg, fromAddress):
    toAddress = 'redmine@myIntranet.intranet' # The 'To' address that Redmine emails should be sent to
    try:
        message = email.message_from_string(msg)
    except:
        print ("Cant set message variable with message_from_string")
        try:
            print raw_message
            f = FeedParser()
            f.feed(data[0][1])
            message = f.close()
            print "set via parser"
        except:
            print ("Can not set message variable")        
    try:
        message.replace_header("From", fromAddress)
    except:
        print ("couldn't replace From, setting instead")
        message.header.append("From", fromAddress)
    print ("setting new To with " + toAddress)
    try:
        message.replace_header("To", toAddress)
    except:
        print ("couldn't replace To, setting instead")
        message.header.append("To", toAddress)
    server = smtplib.SMTP_SSL('myMailServer.myIntranet.intranet', 465) # Internal Email Server settings
    server.set_debuglevel(1)
    server.ehlo()
    server.sendmail(fromAddress, toAddress, message.as_string())
    server.quit()
    print ("Sent an email")

def main():
    print ("Checking")
    checkMail()

set_proc_name("Connector")
main()
