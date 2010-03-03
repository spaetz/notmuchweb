#!/usr/bin/env python
"""
    (c) 2010 Sebastian Spaeth Sebastian@SSpaeth.de
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess, re, logging, os, sys, time, email.utils
import simplejson as json

#---------------------------------------------------------------------------
class Message:
#---------------------------------------------------------------------------
    """
    Represents a message as returned by notmuch.

    - Valid instance variables self.*:
      The following vars are set on the initial parsing:
      .id (msg id, is set on the initial parsing)
      .file (full file name including path, is set on the initial parsing)
      .tags: a set() of MailDir flags
      .notmuchtags: a set() of notmuch tags

      If the following two variables contain a set() of tags/flags that are 
      different from .tags .notmuchtags, a sync_msg_tags will write those 
      changes:
      .sync_tags: a set() of MailDir flags to be used
      .sync_notmuchtags: a set() of notmuch tags to be used

      .valid: is True if parsing found a message, False otherwise
    """

    def __init__(self, nm_msg):
       """inititialize a message from "nm_msg" (output from notmuch show 
       in json format.
       """
       self.valid=False
       self.msg=None
       self.maildirflags = self.sync_maildirflags = None
       self.tags = self.sync_tags = None
       self.parse(nm_msg)
       self.date = None

    def parse(self, message):
        if message == "":
            logging.debug("Message.parse() was handed an empty text.")
            return
        #message[0][0].keys()=[u'body', u'tags', u'filename', u'headers', u'id', u'match']
        if set((u'tags', u'filename', u'id')) < set(message[0][0].keys()):
            self.valid=True
            self.msg = message[0][0]
            self.tags = message[0][0]['tags']
            flags = re.sub('^.*:[12],([A-Z]*)$','\\1',self.file)
            self.maildirflags = set(flags)
            #self.date will get lazily parsed when needed
        else:
            #TODO better output here
            logging.warning("no valid mail")

    @property
    def file(self):
        return self.msg.get('filename', None)

    @property
    def header(self):
        return self.msg['headers']

    @property
    def Subject(self):
        return self.msg['headers'].get('Subject', None)

    @property
    def From(self):
        return self.msg['headers'].get('From', None)

    @property
    def realName(self):
        addr = email.utils.parseaddr(self.From)
        if (addr[0] == ''):
            return addr[1]
        return addr[0]

    @property
    def mailAddress(self):
        return email.utils.parseaddr(self.From)[1]

    @property
    def body(self):
        return self.msg.get('body', None)

    def get_date(self, format):
        if self.date is None:
            self.date = email.utils.parsedate(self.Date)
        return time.strftime(format, self.date)

    @property
    def Date(self):
        return self.msg['headers'].get('Date', None)

    @property
    def id(self):
        return self.msg.get('id', None)

    def get_tags(self):
        return self.get('_tags', None)
    def set_tags(self, tags):
        self._tags = set(tags)
    tags = property(get_tags, set_tags)
        

    def __repr__(self):
        """A message is represented by "id:blah" (if valid) or 'NULL' """
        if not self.valid or hasattr(self,"id") == True:
            return "NULL"
        return "id:%s" % (self.id)

    def sync_msg_tags(self, dryrun=False):
        """ Sync up changed maildir tags and/or notmuch tags.
        It examines self.tags|sync_tags and self.maildirflags|sync_maildirflags
        sync_* contains the new set of tags to be applied
        """

        if (self.sync_maildirflags is not None and self.maildirflags ^ self.sync_maildirflags):
            #sync_tags differs from tags. Need to sync up maildir tags
            newtags = "".join(sorted(self.sync_maildirflags))
            newfile = re.sub(r'^(.*:[12],)([A-Z]*)$',"\\1"+newtags,self.file)
            logging.debug("Maildir flags for %s (%s -> '%s')" % 
                          (self.id,sorted(self.maildirflags),newtags))
            #check if we need to move from 'new' to 'cur' dir
            if 'S' in self.sync_maildirflags:
                # split BASEDIR / NEW / FILENAME into components
                (path, filename) = os.path.split(newfile)
                (basedir, curdir)= os.path.split(path)
                curdir = re.sub("^new$","cur", curdir)
                newfile = os.path.join(basedir, curdir, filename)

            if not dryrun:
                try:
                    os.rename(self.file, newfile)
                except OSError, e:
                    if e.errno == 2:
                        logging.info("Renaming not possible, file %s not found" % (self.file))
                    else:
                        raise OSError(e)

        if (self.sync_tags is not None
            and self.tags ^ self.sync_tags):
            #sync_notmuchtags differs. Need to sync notmuch tags
            #list of tags to delete and add e.g. ("-inbox -unread")
            modtags  = " ".join(map(lambda x:"-"+x,self.tags - self.sync_tags))
            modtags += " ".join(self.sync_tags - self.tags)

            logging.debug("Sync tag %s for id:%s" % (modtags, self.id))

            if not dryrun:
                #actually modify the notmuch tag database
                process = Notmuch().exec_cmd(["tag",modtags, 
                                  "--", "id:%s" % (self.id)])
                (stdout, stderr) = process.communicate()
                if stderr:
                    logging.error("Notmuch failed: %s" % (stderr))

#---------------------------------------------------------------------------
class Messages:
#---------------------------------------------------------------------------
    """
    An iterator containing a bunch of mail messages.
    """

    def __init__(self, nm_messages, keep_body=True):
        """ Initialize Message with nm_messages (output from notmuch show) """
        self.msgs=[]
        if (nm_messages == None):
            #init an empty Messages
            return
        self.parse(nm_messages, keep_body)

    def parse(self, nm_messages, keep_body):
        """ parses nm_messages (output from notmuch show) and adds those
        Message()s to a self.msgs list.
        Returns None if no message was found. True otherwise
        """
        json_msgs = json.loads(nm_messages)
        if len(json_msgs) == 0:
            #TODO:
            logging.warning("Found no valid messages")
            return None

        #parse each single message and append it
        for msg in json_msgs:
            if not keep_body: del(msg[0][0]['body'])
            msg = Message(msg)
            if msg.valid:
                self.msgs.append(msg)

    def __getitem__(self, n):
        """ returns the nth message
        """
        return self.msgs[n]

    def __len__(self):
        """ Returns the number of contained messages """
        return len(self.msgs)

    def __iter__(self):
        #Just return self
        self._iter_pos = 0
        return self

    def next(self):
        """ returns the next message when iterating """
        if (self._iter_pos == len(self.msgs)):
            raise StopIteration     # end of iteration
        self._iter_pos += 1
        return self.msgs[self._iter_pos - 1]

    def __repr__(self):
        return "\n".join([str(msg) for msg in self.msgs])

#---------------------------------------------------------------------------
class Notmuch:
#---------------------------------------------------------------------------
    """
    python abstraction to the notmuch command line interface. 
    It uses the logging module for logging, 
    so you can set that up to log to files etc.
    """
    __notmuchcmd__ = "notmuch"

    def __init__(self, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger()

    def exec_cmd(self, cmdoptions):
        """ Execute a notmuch command and return the 'process'.
        cmdoptions is a list of command options to notmuch. You will 
        usually finish the prosess with something like:
        (stdout, stderr) = process.communicate()
        """
        logging.debug("Execute %s" % ([Notmuch.__notmuchcmd__] + cmdoptions))

        process = subprocess.Popen([Notmuch.__notmuchcmd__] + cmdoptions, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return process


    def new(self):
        """ Perform a notmuch new in order to get a consistent db
        Returns True on success or None on error
        """
        cmdoptions = ['new']
        process = self.exec_cmd(cmdoptions)
        (stdout, stderr) = process.communicate()

        if process.returncode != 0:
            logging.warning("Notmuch new failed (returns: %d): %s" %
                          (process.returncode, stderr))
            return None
        return True

    def show(self, term):
        """searches notmuch for "term"
        Returns Messages() will even return sth on an xapian error,
        as not all of them are fatal and some occur frequently...
        """
        cmdoptions = ['show', '--format=json', term]
        process = self.exec_cmd(cmdoptions)
        (stdout, stderr) = process.communicate()

        if process.returncode != 0:
            logging.warning("Notmuch show failed (xapian returns: %d). We probably not return all positive search results.\n%s" %
                          (process.returncode, stderr))
            #Don't abort here... not returning None

        # parse notmuch return and return Message or (Message1, Message2,...)
        msgs = Messages(stdout)
        return msgs

    def search(self, term):
        print("Not implemented yet")

    def prune(self, criteria="tag:delete or tag:maildir::trashed", dryrun=False):
        """ Physically delete all mail files matching 'tag'. 
        Returns the number of matched mails.
        If dryrun == True, it will not actually delete them.
        """
        del_msgs = self.show(criteria)
        len_del_msgs = len(del_msgs)

        if del_msgs == None:
            logging.error("Could not prune messages due to notmuch error.")
            return None

        if not dryrun:
            deleted = 0
            for m in del_msgs:
                success = self.unlink_file(m)
                deleted += success
            self.logger.info("Deleted %d of %d messages." %
                             (deleted, len_del_msgs))
        else:
            self.logger.info("Would have deleted %d messages." %
                             (len_del_msgs))
        return len_del_msgs

    def unlink_file(self,m):
        """ returns 1 on success, or 0 otherwise.
        Does not fail if the file does not exist."""
        logging.debug("Delete %s" % (m.file))
        try:
            os.unlink(m.file)
        except OSError, e:
            if e.errno == 2:
                logging.info("File %s not found for deletion." % (m.file))
                return 0
            else:
                raise OSError(e)
        return 1

    def syncTags(self,thorough=False, frommaildir=False,dryrun=False, all_mails=None):
        """ sync the unread Tags. It does not really go through all mail files,
        but compares the stored file name with the notmuch tags.
        It will take the maildir tags as authoritative if 'frommaildir' or 
        the notmuch tags otherwise. 
        
        Flags handled:
        * "S": the user has viewed this message. Corresponds to "unread" tag
        * "T" (deleted): the user has moved this message to the trash.
        * "D" (draft):
        * "F" (flagged): user-defined flag; toggled at user discretion. 
        Not handled:
        * Flag "P" (passed): the user has resent/forwarded/bounced this message.
        * Flag "R" (replied): the user has replied to this message.
        """
        if not all_mails:
            #search for messages from beginning of last month until 2036
            # (we have a  year 2036 problem)
            searchterm = "date:lastmonth..2036"
        else:
            #search for all messages between year 0 and 2036 
            # (we have a  year 2036 problem)
            searchterm = "date:1970..2036"
        msgs = self.show(searchterm)

        if msgs == None:
            logging.error("Could not sync messages due to notmuch error.")
            return None

        tag_trans={'delete':'T','draft':'D','flagged':'F'}
        tag_trans_inverse = dict((tag_trans[x], x) for x in tag_trans) # a bit clumsy ?!
        # check all messages for inconsistencies
        num_modified = 0
        for m in msgs:
            modified = False
            # handle SEEN vs unread tags:
            if not (('S' in m.maildirflags) ^ ('unread' in m.tags)):
                modified = True
                if frommaildir:
                    # Flip the unread notmuch tag
                    m.sync_tags = m.tags ^ set(['unread'])
                else:
                    # Flip the SEEN maildir tag
                    m.sync_maildirflags = m.maildirflags ^ set(['S'])

            #handle all other tag consistencies
            #these MailDir flags in tag_trans are wrong
            wrongflags = (set([tag_trans.get(x) for x in m.tags]) \
                          ^ set(tag_trans.values()) & m.maildirflags ) \
                          - set([None])     # finally remove None from result
            if wrongflags:
                modified = True
                if frommaildir:
                    # Flip the maildir flags
                    if m.sync_tags == None:
                        m.sync_tags = set()
                    m.sync_tags = m.sync_tags | m.tags ^ \
                        set ([tag_trans_inverse.get(x) for x in wrongflags])
                    #logging.debug("Flip nm %s to %s (flags %s)" % 
                    #            (m.tags,m.sync_tags, wrongflags))
                else:
                    # Flip the maildir flags
                    if m.sync_maildisrflags == None:
                        m.sync_maildirflags = set()
                    m.sync_maildirflags = m.sync_maildirflags | (m.maildirflags ^ wrongflags)
                    #logging.debug("Flip f %s to %s %s (notmuch %s)" % 
                    #           (m.maildirflags,m.sync_maildirflags, wrongflags, m.tags))

            if modified:
                num_modified += 1 
                m.sync_msg_tags(dryrun=dryrun)

        logging.info("Synced %d messages. %d modified." % (len(msgs), num_modified))

###----------------------------------------------------------------------------
import web
from web.contrib.template import render_jinja

urls = (
    '/', 'index',
    '/show/(.*)', 'show_msgs',
    '/id:(.*)', 'show_msg_by_id',
)

render = render_jinja(
        'templates',   # Set template directory.
        encoding = 'utf-8'
    )
app = web.application(urls, globals())

class index:
    def GET(self):
        return show_msgs().GET('tag:inbox',index=True)

class show_msg_by_id:
    def GET(self, id):
        return show_msgs().GET('id:'+id, index=False)

class show_msgs:
    def GET(self, query, index=True):
        notmuch = Notmuch()
        msgs = notmuch.show(query)
        if index:
            return render.list(msgs=msgs)
        else:
            return render.thread(msgs=msgs)

if __name__ == "__main__":
    app.run()
