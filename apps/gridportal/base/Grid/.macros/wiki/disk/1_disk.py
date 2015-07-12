    
def main(j, args, params, tags, tasklet):
    import JumpScale.baselib.units
    ros = j.clients.ros.get()
    diskcl = ros.system.disk
    id = args.getTag('id')
    gid = args.getTag('gid')
    nid = args.getTag('nid')
    if not id:
        out = 'Missing disk id param "id"'
        params.result = (out, args.doc)
        return params

    key = "%s_%s_%s" % (gid, nid, id)
    if not diskcl.exists(key):
        params.result = ('Disk with id %s not found' % id, args.doc)
        return params
    disk = diskcl.get(key)

    def objFetchManipulate(id):
        disk['usage'] = 100 - int(100.0 * float(disk['free']) / float(disk['size']))
        disk['dpath'] = disk['path'] # path is reserved variable for path of request
        disk['bpath'] = j.system.fs.getBaseName(disk['path'])
        disk['name'] = disk['path'].split('/')[-1]
        for attr in ['size', 'free']:
            disk[attr] = "%.2f %siB" % j.tools.units.bytes.converToBestUnit(disk[attr], 'M')
        disk['type'] = ', '.join([str(x) for x in disk['type']])
        # obj['systempids'] = ', '.join([str(x) for x in obj['systempids']])
        return disk

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
