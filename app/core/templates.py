from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import os

templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")

env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html", "xml"]),
)
