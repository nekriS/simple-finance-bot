
class path:
    def __init__(self,
                 folder = "data",
                 path_json = "data/json",
                 default_category_json = "default_categories.json",
                 users_file = "users.json",
                 path_users = "",
                 path_default_category = ""):
        self.folder = folder
        self.path_json = path_json 
        self.default_category_json = default_category_json
        self.users_file = users_file
        self.path_users = path_users
        self.path_default_category = path_default_category

class memory:
    def __init__(self,
                 timezone = 0,
                 cache = {},
                 keyboards = {}):
        self.timezone = timezone
        self.cache = cache
        self.keyboards = keyboards