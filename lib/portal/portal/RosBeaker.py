from beaker.container import NamespaceManager
class RosBeaker(NamespaceManager):
    def __init__(self, id, namespace_args, **kwargs):
        self._namespace = 'system'
        self._category = 'sessioncache'
        self.namespace = id
        self.systemcl = getattr(namespace_args['client'], self._namespace)
        self._client = getattr(self.systemcl , self._category)

    def __getitem__(self, key):
        key = "%s_%s" % (self.namespace, key)
        if self._client.exists(key):
            return self._client.get(key).value
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        nkey = "%s_%s" % (self.namespace, key)
        if 'user' not in value:
            self._remove(key)
            return
        elif value['user'] == 'guest':
            return

        if self._client.exists(nkey):
            item = self._client.get(nkey)
            item.value = value
            self._client.update(item)
        else:
            item = self._client.new()
            item.guid = nkey
            item.value = value
            self._client.set(item)

    def _remove(self, key):
        key = "%s_%s" % (self.namespace, key)
        self._client.delete(key)

    def __contains__(self, key):
        key = "%s_%s" % (self.namespace, key)
        return self._client.exists(key)

    def __delitem__(self, key, **kwargs):
        self._remove(key)

    def acquire_read_lock(self, **kwargs):
        return True

    def release_read_lock(self, **kwargs):
        return True

    def acquire_write_lock(self, **kwargs):
        return True

    def release_write_lock(self, **kwargs):
        return True
