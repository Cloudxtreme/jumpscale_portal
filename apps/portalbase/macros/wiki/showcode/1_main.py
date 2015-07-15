
def main(j, args, params, tags, tasklet):
    params.merge(args)

    codepaths = dict()

    actors = j.core.portal.active.actorsloader.actors
    for actorname, info in actors.iteritems():
        if j.system.fs.exists(info.model.path):
            parent = j.system.fs.getParent(info.model.path)
            parent = parent.replace(j.dirs.baseDir, '$base')
            codepaths[parent] = '%s Actors' % j.system.fs.getBaseName(parent).capitalize()


    codepaths[j.system.fs.joinPaths('$base', 'apps', 'ros', 'models')] = 'Models'

    codepaths[j.system.fs.joinPaths('$jumpscriptsdir', 'jumpscripts')] = 'Jumpscripts'

    result = list()
    result.append('''{{html: <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">}}''')
    for path, title in codepaths.iteritems():
        sectionid = 'collapse_%s' % title.replace(' ', '_')
        headingid = 'heading_%s' % title
        result.append("""{{html:
            <div class="panel panel-default">
<div class="panel-heading" role="tab" id="%s">
  <h4 class="panel-title">
            """ % headingid)
        result.append('<a data-toggle="collapse" data-parent="#accordion" href="#%s" aria-expanded="false" aria-controls="%s">}}' % (sectionid, sectionid))

        result.append(title)
        result.append("""{{html
            </a>
  </h4>
</div>
<div id="%s" class="panel-collapse collapse" role="tabpanel" aria-labelledby="%s">
  <div class="panel-body"> }}
            """ % (sectionid, headingid))

        result.append('{{explorer: ppath:%s}}' % path)
        result.append("""{{html
            </div></div></div>}}""")

    result.append("""{{html
        </div>
        }}""")
    result = '\n'.join(result)
    # result = 'test'
    print result

    params.result = (result, params.doc)
    return params


def match(j, args, params, tags, tasklet):
    return True
