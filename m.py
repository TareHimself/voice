import webview
Window = webview.create_window('Hello world', 'https://umeko.dev/')

webview.start(gui="edgechromium")
Window.evaluate_js('''
return { a : "HELP ME" }''', print)
