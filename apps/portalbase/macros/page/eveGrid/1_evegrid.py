from itertools import count
import json

def main(j, args, params, tags, tasklet):
    page = args.page
    
    hrd = j.core.hrd.get(content=args.cmdstr)
    eveGrid = {
        'specJsonPath': hrd.get('spec.json.path', default='/docs/spec.json'),
        'schemaURL': hrd.getStr('schema.url', default=''),
        'entityName': hrd.get('entity.name', default=''),
        'datetimeFields': hrd.get('datetime.fields', default=""),
    }
    sort = hrd.getDict('sortBy').copy() if hrd.exists('sortBy') else []
    eveGrid['sortBy'] = list()
    for item in sort:
        eveGrid['sortBy'].append((item, int(sort.pop(item))))
    eveGrid['columns'] = []

    hrd_data = hrd.getDictFromPrefix('column')

    for _,columndata in hrd_data.iteritems():
        column = {}
        column['data'] = columndata.get('data', '')
        column['header'] = columndata.get('header', '')
        column['format'] = columndata.get('format', '')
        print '****', column
        eveGrid['columns'].append(column)

    eveGrid['columns'] = (json.dumps(eveGrid['columns'])) or []
    # eveGrid['columns'] = eveGrid['columns'].replace("'", "\'")
    # Add our static resources only once to the page
    if '/system/.files/lib/evegrid/css/eve-grid.css' not in str(page):
        page.addCSS('/jslib/jquery/jqueryDataTable/css/dataTables.bootstrap.css')
        page.addCSS('/system/.files/lib/evegrid/css/eve-grid.css')
        page.addCSS('/jslib/bootstrap/css/bootstrap-datetimepicker.min.css')        
        page.addJS('/jslib/jquery/jqueryDataTable/js/jquery.dataTables.js')
        page.addJS('/jslib/angular/angular1-3-0.min.js')
        page.addJS('/jslib/bootstrap/js/bootstrap.min.js')
        page.addJS('/jslib/underscore/underscore-min.js')
        page.addJS('/jslib/jquery/jqueryDataTable/js/dataTables.bootstrap.js')
        page.addJS('/jslib/moment.js')
        page.addJS('/jslib/bootstrap/js/bootstrap-datetimepicker.js')
        page.addJS('/jslib/spin.min.js')
        page.addJS('/system/.files/lib/evegrid/js/eve-grid.js')
    
    grid = '''
        <div class="container eve-grid-container">
        <div id="{entityName}-container" eve-grid eve-url={schemaURL} eve-entity="{entityName}" eve-spec-path="{specJsonPath}" datetime-fields={datetimeFields} columns='{columns}' sortBy="{sortBy}">
        </div>
        <div id="confirmModal" class="modal fade">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                                <h4 class="modal-title">Confirmation</h4>
                            </div>
                            <div class="modal-body">
                                <p>Are you sure you want to delete?</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                                <button type="button" class="btn btn-danger confirmDelete">Delete</button>
                            </div>
                        </div>
                    </div>
                </div>
    </div>

     '''

    grid = grid.format(**eveGrid)

    page.addMessage(grid)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
