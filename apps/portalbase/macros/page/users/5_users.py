
import datetime

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    userdetails = '/system/user?id'

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        if tag == 'userdetails':
            userdetails = val
            continue
        if isinstance(val, list):
            val = ', '.join(val)
        filters[tag] = val

    fieldnames = ['ID', 'Email', 'Domain', 'Roles', 'Groups', 'Description', 'Active']

    def makeLink(row, field):
        return '[%s|%s=%s]' % (row[field], userdetails, row['guid'])

    fieldids = ['id', 'emails', 'domain', 'roles', 'groups', 'description', 'active']
    fieldvalues = [makeLink, 'emails', 'domain', 'roles', 'groups', 'description', 'active']
    tableid = modifier.addTableForModel('system', 'user', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
