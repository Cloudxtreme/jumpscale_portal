import datetime

def main(j, args, params, tags, tasklet):
    import JumpScale.baselib.units
    ros = j.clients.ros.get()
    id = args.getTag('id')
    gid = args.getTag('gid')
    if not id or not gid:
        out = 'Missing vdisk id param "id"'
        params.result = (out, args.doc)
        return params

    vdisk = ros.system.vdisk.get('%s_%s' % (gid, id))
    if not vdisk:
        params.result = ('VDisk with id %s not found' % id, args.doc)
        return params

    def objFetchManipulate(id):
        obj = vdisk
        for attr in ['lastcheck', 'expiration', 'backuptime']:
            value = obj.get(attr)
            if value: 
                obj[attr] = datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
            else:
                obj[attr] = 'N/A'
        for attr in ['size', 'free', 'sizeondisk']:
            size, unit = j.tools.units.bytes.converToBestUnit(obj[attr], 'K')
            if unit:
                unit += "i"
            obj[attr] = "%s %sB" % (size, unit)
        return obj

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
