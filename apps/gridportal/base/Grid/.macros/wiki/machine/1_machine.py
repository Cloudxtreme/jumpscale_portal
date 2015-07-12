import datetime

def main(j, args, params, tags, tasklet):
    ros = j.clients.ros.get()
    machinecl = ros.system.machine
    id = args.getTag('id')
    gid = args.getTag('gid')
    if not id:
        out = 'Missing machine id param "id"'
        params.result = (out, args.doc)
        return params

    machine = machinecl.get("%s_%s" % (gid, id))
    if not machine:
        params.result = ('Machine with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = machine
        for attr in ['roles', 'ipaddr']:
            obj[attr] = ', '.join([str(x) for x in obj[attr]]) 

        netaddr = obj['netaddr']
        netinfo = ''
        for k, v in netaddr.iteritems():
            netinfo += 'mac address: %s, interface: %s, ip: %s<br>' % (k, v[0], v[1])
        obj['netaddr'] = netinfo

        obj['lastcheck'] = datetime.datetime.fromtimestamp(obj['lastcheck']).strftime('%Y-%m-%d %H:%M:%S')
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
