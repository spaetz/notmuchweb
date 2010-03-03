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
