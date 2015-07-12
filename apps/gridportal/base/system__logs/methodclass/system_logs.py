from JumpScale import j
import JumpScale.baselib.serializers


class system_logs(j.code.classGetBase()):

    def __init__(self):
        self._te = {}
        self.actorname = "logs"
        self.appname = "system"

    def listJobs(self, **args):

        nip = 'localhost'
        if args.get('nip'):
            nip = args.get('nip')
        ros = j.clients.ros.get()
        client = ros.system.job

        params = {'ffrom': '', 'to': '', 'nid': '', 'gid': '',
                  'parent': '', 'state': '', 'jsorganization': '', 'jsname': '', 'roles': ''}
        for p in params:
            params[p] = args.get(p)

        if not any(params.values()):
            jobs = client.search({})
        else:
            query = {'query': {'bool': {'must': list()}}}
            if params['ffrom']:
                ffrom = params.pop('ffrom')
                starting = j.base.time.getEpochAgo(ffrom)
                drange = {'range': {'timeStart': {'gte': starting}}}
                query['query']['bool']['must'].append(drange)
            if params['to']:
                to = params.pop('to')
                ending = j.base.time.getEpochAgo(to)
                if query['query']['bool']['must']:
                    query['query']['bool']['must'][0]['range']['timeStart']['lte'] = ending
                else:
                    drange = {'range': {'timeStart': {'lte': ending}}}
                    query['query']['bool']['must'].append(drange)
            if params['roles']:
                roles = params.pop('roles')
                query_string = {"query_string":{"default_field":"roles","query": roles}}
                query['query']['bool']['must'].append(query_string)
            for k, v in params.iteritems():
                if v:
                    if k == 'state':
                        v = v.lower()
                    term = {'term': {k: v}}
                    query['query']['bool']['must'].append(term)

            jobs = client.search(query)

        aaData = list()
        fields = ('jsname', 'jsorganization', 'parent', 'roles', 'state')
        for item in jobs['result']:
            itemdata = list()
            for field in fields:
                itemdata.append(item['_source'].get(field))
            itemargs = j.db.serializers.ujson.loads(item['_source'].get('args', {}))
            itemdata.append('<a href=%s>%s</a>' % ('/gridlogs/job?jobid=%s' % item['_id'], itemargs.get('msg', '')))
            result = item['_source'].get('result', '{}')
            result = j.db.serializers.ujson.loads(result if result else '{}')
            itemdata.append(result)
            aaData.append(itemdata)
        return {'aaData': aaData}



    def listNodes(self, **args):
        ros = j.clients.ros.get()
        client = ros.system.node
        
        nodes = client.search('null')

        aaData = list()
        fields = ('name', 'roles', 'ipaddr', 'machineguid')
        for item in nodes['result']:
            itemdata = list()
            for field in fields:
                itemdata.append(item['_source'].get(field))
            itemdata.append(item.get('_id'))
            ipaddr = item['_source'].get('ipaddr')[0] if item['_source'].get('ipaddr') else ''
            itemdata.append('<a href="/grid/node?nip=%s">link</a>' % ipaddr)
            aaData.append(itemdata)
        return {'aaData': aaData}


    def listECOs(self, **args):
        import JumpScale.baselib.elasticsearch
        esc = j.clients.elasticsearch.get()

        nid = 1
        if args.get('nip'):
            nid = args.get('nid')
        query = {"query":{"bool":{"must":[{"term":{"nid":nid}}]}}}
        ecos = esc.search(query, index='system_eco')

        aaData = list()
        fields = ('appname', 'category', 'epoch', 'errormessage', 'jid', 'level', 'backtrace', 'nid', 'pid')

        for item in ecos['hits']['hits']:
            itemdata = list()
            for field in fields:
                itemdata.append(item['_source'].get(field))
            aaData.append(itemdata)

        if not aaData:
            aaData = [None, None, None, None, None]
        return {'aaData': aaData}


    def listLogs(self, **args):
        import JumpScale.baselib.elasticsearch
        esc = j.clients.elasticsearch.get()

        query = 'null'
        if args.get('nid'):
            nid = args.get('nid')
            query = {"query":{"bool":{"must":[{"term":{"nid":nid}}]}}}

        logs = esc.search(query, index='system_log')

        aaData = list()
        fields = ('appname', 'category', 'epoch', 'message', 'level', 'pid')

        for item in logs['hits']['hits']:
            itemdata = list()
            for field in fields:
                itemdata.append(item['_source'].get(field))
            aaData.append(itemdata)
        return {'aaData': aaData}
