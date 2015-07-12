from JumpScale import j
from JumpScale.portal.portal import exceptions
import ujson as json
import time
import types

clients = dict()


def getClient(namespace):
    if namespace not in clients:
        ros = j.clients.ros.get()
        client = getattr(ros, namespace)
        clients[namespace] = client
    return clients[namespace]


def doAudit(user, path, kwargs, responsetime, statuscode, result):
    client = getClient('system')
    audit = client.audit.new()
    audit.user = user
    audit.call = path
    audit.statuscode = statuscode
    audit.args = json.dumps([])  # we dont want to log self
    auditkwargs = kwargs.copy()
    auditkwargs.pop('ctx', None)
    audit.kwargs = json.dumps(auditkwargs)
    if not isinstance(result, types.GeneratorType):
        audit.result = json.dumps(result)
    else:
        audit.result = json.dumps('Result of type generator')

    audit.responsetime = responsetime
    client.audit.set(audit)


class AuditMiddleWare(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_response):
        statinfo = {'status': 200}
        def my_response(status, headers, exc_info=None):
            statinfo['status'] = int(status.split(" ", 1)[0])
            return start_response(status, headers, exc_info)

        start = time.time()
        result = self.app(env, my_response)
        responsetime = time.time() - start
        audit = env.get('JS_AUDIT')
        if audit or statinfo['status'] >= 400:
            ctx = env.get('JS_CTX')
            user = env['beaker.session'].get('user', 'Unknown')
            kwargs = ctx.params.copy() if ctx else {}
            doAudit(user, env['PATH_INFO'], kwargs, responsetime, statinfo['status'], result)
        return result

class auth(object):

    def __init__(self, groups=None, audit=True):
        if isinstance(groups, str):
            groups = [groups]
        if groups is None:
            groups = list()
        self.groups = set(groups)
        self.audit = audit

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if 'ctx' not in kwargs:
                # call is not performed over rest let it pass
                return func(*args, **kwargs)
            ctx = kwargs['ctx']
            user = ctx.env['beaker.session']['user']
            if self.groups:
                userobj = j.core.portal.active.auth.getUserInfo(user)
                groups = set(userobj.groups)
                if not groups.intersection(self.groups):
                    raise exceptions.Forbidden('User %s has no access. If you would like to gain access please contact your adminstrator' % user)

            ctx.env['JS_AUDIT'] = self.audit
            return func(*args, **kwargs)
        return wrapper
