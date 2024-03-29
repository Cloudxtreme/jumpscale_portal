import os

def main(j, args, params, tags, tasklet):
    params.result = page = args.page

    try:
        spaces = j.core.portal.active.getSpaces()
        for space_name in spaces:
            space = j.core.portal.active.getSpace(space_name, ignore_doc_processor=True)
            space_path = os.path.abspath(space.model.path)
        j.system.process.execute('cd %s;git pull' % space_path)
        page.addMessage('Pulled and Updated')
    except Exception, error:
        page.addMessage('Something went wrong with updating one more or more of the spaces')

    return params


def match(j, args, params, tags, tasklet):
    return True