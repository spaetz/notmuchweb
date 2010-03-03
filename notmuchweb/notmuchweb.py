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
from notmuch import Notmuch
import web
from web.contrib.template import render_jinja

urls = (
    '/', 'index',
    '/show/(.*)', 'show_msgs',
    '/search/(.*)', 'show_threads',
    '/id:(.*)', 'show_msg_by_id',
)

render = render_jinja(
        'templates',   # Set template directory.
        encoding = 'utf-8'
    )
app = web.application(urls, globals())

class index:
    def GET(self):
        return show_msgs().GET('tag:inbox',threads=False)

class show_threads:
    def GET(self, query):
        return show_msgs().GET(query, threads=True)

class show_msg_by_id:
    def GET(self, id):
        return show_msgs().GET('id:'+id, threads=False, detail=True)

class show_msgs:
    def GET(self, query, threads=False, detail=False):
        notmuch = Notmuch()
        msgs = notmuch.show(query,wholeThread=threads)
        if detail:
            return render.thread(msgs=msgs)
        else:
            return render.list(msgs=msgs)

if __name__ == "__main__":
    app.run()
    #print Notmuch().show('from:osm-list@deelkar.net')
