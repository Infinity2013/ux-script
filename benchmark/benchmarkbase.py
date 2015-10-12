from uiautomator import device as d


class benchmarkbase():

    def res_id_text(self, id):
        return d(resourceId='%s' % id).info.get("text")
