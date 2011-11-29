#!/usr/bin/env python

import json
import os
import logging

import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


##########   /*     */   ##########


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/add", AddHandler),
            (r"/admin", AdminHandler),
            (r"/album/(\d+)?/?", AlbumHandler),
            (r"/auth/login", AuthHandler),
            (r"/auth/logout", LogoutHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login"
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        else:
            return tornado.escape.json_decode(user_json)


##########   /*     */   ##########


class AuthHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Google auth failed")
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.redirect(self.get_argument("next", "/"))

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")


##########   /*     */   ##########


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html")

class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("admin.html")

class AlbumHandler(BaseHandler):
    def get(self, post_id):
        if post_id:
            print post_id
        else:
            self.redirect("/")

class AddHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user['email'] == "chrisallick@gmail.com":
            self.render("add.html")
        else:
            print "nope"

    @tornado.web.authenticated
    def post(self):
        if self.current_user['email'] != "chrisallick@gmail.com":
            album = self.get_argument('album', None)
            if album:
                a = json.loads( album )
                artist = a['artist']
                try:
                    f = open('/Users/chrisallick/Documents/GIT/sellmymusic/static/albums/'+artist+'.json', 'w')
                    f.write( json.dumps(a) )
                except IOError as ioe:
                    print "error writing json file"
                    print ioe
                else:
                    f.close()

                self.write( json.dumps({'msg': 'success'}) );
        else:
            self.write( json.dumps({'msg': 'error'}) );


##########   /*     */   ##########


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()