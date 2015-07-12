from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):

    params.result = page = args.page
    userguid = args.getTag('guid')
    ros = j.clients.ros.get()
    scl = ros.system
    user = scl.user.get(userguid)

    popup = Popup(id='user_edit', header='Change User', submit_url='/restmachine/system/usermanager/editUser')

    options = list()
    popup.addText('Enter emails (comma seperated)', 'emails')
    popup.addText('Enter domain', 'domain')
    popup.addText('Enter Password (leave empty to unchange)', 'password', type='password')
    for group in scl.group.search({})[1:]:
        available = group['id'] in user.groups
        options.append((group['id'], group['id'], available))

    popup.addCheckboxes('Select Groups', 'groups', options)
    popup.addHiddenField('username', user.id)
    popup.write_html(page)

    return params
