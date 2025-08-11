from flask import (
    Flask,
)
import frontmatter
import markdown
from markdown.extensions.toc import TocExtension
from flask_compress import Compress
from search.oligo_search import precache_data


def create_app(
    secret_key,
    message_root,
    template_folder="../templates",
):
    precache_data()
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder=template_folder,
    )
    app.secret_key = secret_key
    app.config["MESSAGE_ROOT"] = message_root
    Compress(app)
    return app


def parse_markdown(content: str):
    return markdown.markdown(
        content,
        extensions=[TocExtension(baselevel=1)]
    )


def load_markdown(path: str):
    with open(path, "r") as f:
        page_data = frontmatter.load(f)
        html = parse_markdown(page_data.content)
        return (html, page_data)
