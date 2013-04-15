#encoding:utf-8

handlers = []
ui_modules = {}

modules = ['index', 'login', 'manager', 'common','search']

for module in modules:
    module = __import__("handlers."+module, fromlist=["handlers"])
    handlers.extend(module.handlers)
    ui_modules.update(module.ui_modules)
