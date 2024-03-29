import datetime

def main(j, args, params, tags, tasklet):
    try:
        import ujson as json
    except:
        import json

    page = args.page

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        if not val:
            continue
        if tag == 'from' and val:
            filters['timeStart'] = {'$gte': j.base.time.getEpochAgo(val)}
        elif tag == 'to' and val:
            filters['timeStop'] = {'$lte': j.base.time.getEpochAgo(val)}
        elif tag == 'organization':
            filters['category'] = val
        elif tag == 'jsname':
            filters['cmd'] = val
        elif tag in ('nid', 'gid') and val:
            filters[tag] = int(val)
        elif tag == 'filter':
            filter = json.loads(val or 'null')
            filters.update(filter)
        elif val:
            filters[tag] = val

    modifier = j.html.getPageModifierGridDataTables(page)
    def makeLink(row, field):
        time = modifier.makeTime(row, field)
        return '[%s|/grid/job?id=%s]'  % (time, row['guid'])

    def makeResult(row, field):
        result = row[field]
        try:
            result = json.loads(result)
        except:
            pass
        return j.html.escape(str(result))

    fieldnames = ['Create Time', 'Start', 'Stop', 'Category', 'Command', 'Queue', 'State']
    fieldvalues = [makeLink, modifier.makeTimeOnly, modifier.makeTimeOnly, 'category', 'cmd', 'queue', 'state']
    fieldids = ['timeCreate', 'timeStart', 'timeStop', 'category', 'cmd', 'queue', 'state']
    tableid = modifier.addTableForModel('system', 'job', fieldids, fieldnames, fieldvalues, nativequery=filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
