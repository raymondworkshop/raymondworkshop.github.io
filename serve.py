import livereload

import blog


def rebuild():
    blog.main()


# rebuild()
server = livereload.Server()
server.setHeader("Cache-Control", "no-store")
server.watch("_posts/*.md", rebuild)
#server.watch("docs/**")
server.watch("templates/**.html", rebuild)
server.serve(root="docs", port=4000)
