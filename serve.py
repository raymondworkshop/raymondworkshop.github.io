import livereload

import blog


def rebuild():
    blog.main()


server = livereload.Server()
server.setHeader("Cache-Control", "no-store")
server.watch("_posts/*.md", rebuild)
server.watch("_site/**")
server.serve(root="_site")
