import datetime

def main(j, args, params, tags, tasklet):
    ros = j.clients.ros.get()
    niccl = ros.system.nic
    guid = args.getTag('id')
    if not guid:
        out = 'Missing NIC guid param "guid"'
        params.result = (out, args.doc)
        return params

    nic = niccl.get(guid)
    if not nic:
        params.result = ('NIC with guid %s not found' % guid, args.doc)
        return params

    def objFetchManipulate(id):
        nic['lastcheck'] = datetime.datetime.fromtimestamp(nic['lastcheck']).strftime('%Y-%m-%d %H:%M:%S')
        nic['ipaddr'] = ', '.join([str(x) for x in nic['ipaddr']])
        return nic

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
