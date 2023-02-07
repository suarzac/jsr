"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
from pcconfig import config

import pynecone as pc
docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"

#pola rs implement
import polars as pl
import random

#nba
import plotly.express as px
import plotly.graph_objects as go
from .helpers import navbar

# youtube_overview = "data/USvideos.csv"
# youtube_data = pl.read_csv(youtube_overview)
# categories = sorted(youtube_data["category_id"].unique().drop_nulls().cast(str))

# nba_overview = "https://media.geeksforgeeks.org/wp-content/uploads/nba.csv"
# #
# nba_data = pl.read_csv(nba_overview)
# college = sorted(nba_data["College"].unique().drop_nulls().cast(str))

class baseState(pc.State):
    """The app state."""

    count: int = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1

class FormState(baseState):

    formCount: int = 0

    firstName: str = ""
    lastName: str = ""

    email: str = ""

    submitButton = "this was lower case text"

    def update(self):
        self.formCount = random.randint(0, 100)

def formPage():
    return pc.center(
        pc.vstack(
            navbar(),
            pc.text("Your Form", color_scheme = "blue"),
            pc.divider(),
            pc.text(FormState.formCount),
            pc.hstack(
                pc.form_control(
                    pc.form_label("First Name", html_for="email"),
                    pc.input(on_change = FormState.set_firstName),
                    pc.form_helper_text("This is a help text"),
                    placeholder = "First Name",
                    is_required=True,
                ),
                pc.form_control(
                    pc.form_label("Last Name", html_for="email"),
                    pc.input(on_change = FormState.set_lastName),
                    pc.form_helper_text("This is a help text"),
                    is_required=True,
                ),
            ),
            pc.hstack(
                pc.form_control(
                    pc.form_label("Email", html_for="email"),
                    pc.input(on_change = FormState.set_email),
                    pc.form_helper_text("This is a help text"),
                    is_required=True,
                ),
            ),
            pc.hstack(
                    pc.button(
                    "Submit",
                    color_scheme="green",
                    variant="outline",
                    border_radius="1em",
                    on_click = FormState.update
                ),
                pc.button(
                    "Cancel",
                    color_scheme="red",
                    variant="outline",
                    border_radius="1em"
                ),
            ),
            
        ),
        padding_top = "10%"
    )
    
def test():
    return pc.center(
        pc.vstack(
            navbar(),
            pc.divider(),
            pc.hstack(
                pc.button(
                    "Decrement",
                    color_scheme="red",
                    border_radius="1em",
                    on_click=baseState.decrement,
                ),
                pc.heading(baseState.count, font_size="2em"),
                pc.button(
                    "Increment",
                    color_scheme="green",
                    border_radius="1em",
                    on_click=baseState.increment,
                ),
            ),
        ),
        padding_top="10%",
    )





def custom():
    return pc.text("Custom Route")


app = pc.App(state=baseState)

# app.add_page(index, title="Test JSR")
app.add_page(test)
app.add_page(formPage, route="/custom-form")
# app.add_page(about)
app.add_page(custom)

app.compile()
