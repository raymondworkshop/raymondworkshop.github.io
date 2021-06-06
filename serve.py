import livereload

import blog


def rebuild():
    blog.main()


# rebuild()
server = livereload.Server()
server.setHeader("Cache-Control", "no-store")
server.watch("_posts/*.md", rebuild)
server.watch("_site/**.html")
server.serve(default_filename="_site/index.html", port=4000)
