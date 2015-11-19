from JumpScale import j

typemap = {'str': 'string',
           'int': 'integer',
           'float': 'float',
           'dict(str)': 'dict',
           'dict': 'dict',
           'list(str)': 'list',
           'list': 'list',
           'list(int)': 'list',
           'bool': 'boolean'}

def generateDomain(spec):
    domain = dict()
    for modelname, modelspec in spec.items():
        domain[modelname] = generateModel(modelspec)
    return domain


def generateModel(modelspec):
    schema = dict()
    model = {'item_url': 'regex("[a-f0-9]+")',
            'item_lookup_field': '_id',
            'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'], 
            'resource_methods': ['GET', 'POST', 'DELETE'], 
            'url': modelspec['name'],
            'schema': schema}
    prop = {'type': 'string', 'default':'', 'required': True}
    schema['guid'] = prop
    
    for propspec in modelspec["properties"]:
        prop = dict()
        schema[propspec['name']] = prop
        ttype=propspec["type"]
        default=propspec["default"]
        args=""
        if default==None:
            prop['default'] = ""
            prop['required'] = True
        else:
            prop['default'] = default
            prop['required'] = False
        if ttype.startswith('list'):
            ttype = 'list'
        elif ttype.startswith('dict'):
            ttype = 'dict'
        prop['type'] = typemap[ttype] 
        continue

        if ttype.find("list")==0:
            ttype=ttype.split("(",1)[1]
            ttype=ttype.split(")",1)[0]
            args+=help_str
            args=args.rstrip(",")
            out+="    %s =  ListField(%s(), default=list,%s)\n"%(name,type2typestr(ttype),args)

        elif ttype.find("dict")==0:
            ttype=ttype.split("(",1)[1]
            ttype=ttype.split(")",1)[0]
            args+=help_str
            args=args.rstrip(",")
            out+="    %s =  ListField(field=%s(), default=list,%s)\n"%(name,type2typestr(ttype),args)
            
        else:
            args+=required_str
            args+=default_str
            args+=help_str
            args=args.rstrip(",")
            out+="    %s = %s(%s)\n"%(name,type2typestr(ttype),args)


    return model
