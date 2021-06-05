import livereload

import build


def rebuild():
    build.main()


server = livereload.Server()
server.setHead("Cache-Control", "no-store")
server.watch("_posts/*.md", rebuild)
server.watch("_site/**")
server.serve(root="_site")
