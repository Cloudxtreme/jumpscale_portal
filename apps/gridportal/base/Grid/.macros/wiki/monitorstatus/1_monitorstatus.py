import JumpScale.grid.gridhealthchecker
import JumpScale.baselib.units
import JumpScale.baselib.redis
import ujson

def main(j, args, params, tags, tasklet):
    doc = args.doc
    import time
    now = time.time()
    nid = args.getTag('nid')
    nidint = int(nid)

    out = list()
    classmap = {'OK': 'success',
                'WARNING': 'warning',
                'EXPIRED': 'warning',
                'UNKNOWN': 'default',
                'HALTED': 'danger',
                'ERROR': 'danger'}

    def makeStatusLabel(status, guid=None):
        html = '<span class="label label-%s pull-right">%s</span>' % (classmap.get(status, 'default'), status)
        if guid:
            html = '<a href="/grid/job?id=%s">%s</a>' % (guid, html)
        return html

    results = j.core.grid.healthchecker.fetchMonitoringOnNode(nidint)
    _, oldestdate = j.core.grid.healthchecker.getErrorsAndCheckTime(results)

    out.append('Node was last checked at: {{ts:%s}}' % oldestdate)

    out.append('{{html: <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">}}')
    noderesults = results.get(nidint, dict())
    for category, data in sorted(noderesults.items()):
        sectionid = 'collapse_%s' % category.replace(' ', '_')
        headingid = 'heading_%s' % category
        table = "||Message||Last Executed||Interval||Status||\n"
        categorystatus = "OK"
        for dataitem in data:
            if isinstance(dataitem, dict):
                status = dataitem.get('state')
                wikistatus = j.core.grid.healthchecker.getWikiStatus(status)
                if categorystatus != 'ERROR' and status !='OK':
                    categorystatus = status
                lastchecked = dataitem.get('lastchecked', '')
                status = makeStatusLabel(status, dataitem.get('guid'))
                if lastchecked:
                    lastchecked = '%s ago' % j.base.time.getSecondsInHR(now - lastchecked)
                interval = dataitem.get('interval')
                if interval:
                    interval = j.base.time.getSecondsInHR(interval)
                else:
                    interval = ''

                table += '|%s |%s |  %s|{{html: %s}} |\n' % (dataitem.get('message', ''), lastchecked, interval, status)
            else:
                table += dataitem
        html = '''{{html:
<div class="panel panel-default">
    <div class="panel-heading" role="tab" id="%(headingid)s">
        <h4 class="panel-title">
            <a data-toggle="collapse" data-parent="#accordion" href="#%(sectionid)s" aria-expanded="false" aria-controls="%(sectionid)s">
                %(category)s
            </a>
            %(status)s
        </h4>
    </div>
    <div id="%(sectionid)s" class="panel-collapse collapse" role="tabpanel" aria-labelledby="%(headingid)s">
        <div class="panel-body">
}}
%(table)s
{{html:
        </div>
    </div>
</div>
}}
''' % {'headingid': headingid, 'sectionid': sectionid, 'table': table,
         'category': category, 'status': makeStatusLabel(categorystatus)}

        out.append(html)


    out.append('{{html: </div>}}')

    out = '\n'.join(out)
    params.result = (out, doc)
    return params


def match(j, args, params, tags, tasklet):
    return True


