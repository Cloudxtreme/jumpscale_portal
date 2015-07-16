
try:
    import ujson as json
except:
    import json
def main(j, args, params, tags, tasklet):
    #macro puts obj info as params on doc, when show used as label, shows the content of the obj in nicely structured code block
    nid = args.getTag('id')
    gid = args.getTag('gid')
    if not nid or not gid:
        params.result = ('Node "id" and "gid" must be passed.', args.doc)
        return params
    gid = int(gid)
    ros = j.clients.ros.get()

    node = None
    if ros.system.node.exists('%s_%s' % (gid, nid)):
        node = ros.system.node.get('%s_%s' % (gid, nid))
    grid = {'name': 'N/A'}
    if ros.system.grid.exists(gid):
        grid = ros.system.grid.get(gid)
    if not node:
        params.result = ('Node with and id %s_%s not found' % (gid, nid), args.doc)
        return params

    def objFetchManipulate(id):
        #obj is a dict
        node["ipaddr"]=", ".join(node["ipaddr"])
        node["roles"]=", ".join(node["roles"])

        r=""
        for netitem in node["netaddr"]:
            dev = netitem['name']
            ip = netitem['ip']
            mac = netitem['mac']
            r+="|%-15s | %-20s | %s| \n"%(dev,mac,ip)
        node["netaddr"]=r
        node['gridname'] = grid['name']
        node['nodename'] = node['name']
        res = node._dump()
        res.update(node.__dict__)
        return res

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)


def match(j, args, params, tags, tasklet):
    return True


