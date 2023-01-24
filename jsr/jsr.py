"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
from pcconfig import config

import pynecone as pc
docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"

#pola rs implement
import polars as pl

#nba
import plotly.express as px
import plotly.graph_objects as go
from .helpers import navbar

nba_overview = "https://media.geeksforgeeks.org/wp-content/uploads/nba.csv"
#
nba_data = pl.read_csv(nba_overview)
college = sorted(nba_data["College"].unique().drop_nulls().cast(str))


class State(pc.State):
    """The app state."""

    count: int = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1
# nba
    position: str
    college: str
    age: list = [0, 50]
    salary: list = [0, 25000000]

    @pc.var
    def df(self) -> pl.DataFrame:
        """The data."""
        # nba = nba_data[
        #     (nba_data["Age"] > int(self.age[0]))
        #     & (nba_data["Age"] < int(self.age[1]))
        #     & (nba_data["Salary"] > int(self.salary[0]))
        #     & (nba_data["Salary"] < int(self.salary[1]))
        # ]

        nba = nba_data.filter(
            (nba_data["Age"] > int(self.age[0]))
            & (nba_data["Age"] < int(self.age[1]))
            & (nba_data["Salary"] > int(self.salary[0]))
            & (nba_data["Salary"] < int(self.salary[1])) 
        )

        if self.college and self.college != "All":
            # nba = nba[nba["College"] == self.college]
            nba = nba[nba["College"] == self.college]

        if self.position and self.position != "All":
            # nba = nba[nba["Position"] == self.position]
            nba = nba[nba["Position"] == self.position]

        # if nba.empty:
        #     return pd.DataFrame()
        # else:
        #     return nba.fillna("")

        if nba.is_empty():
            return pl.DataFrame()
        else:
            return nba.fill_nan("")

    @pc.var
    def scat_fig(self) -> go.Figure:
        """The scatter figure."""
        nba = self.df

        if nba.is_empty():
            return go.Figure()
        else:
            return px.scatter(
                nba.to_pandas(),
                x="Age",
                y="Salary",
                title="NBA Age/Salary plot",
                color=nba["Position"],
                hover_data=["Name"],
                symbol=nba["Position"],
                trendline="lowess",
                trendline_scope="overall",
            )

    @pc.var
    def hist_fig(self) -> go.Figure:
        """The histogram figure."""
        nba = self.df

        if nba.is_empty():
            return go.Figure()
        else:
            return px.histogram(
                nba.to_pandas(), 
                x="Age", 
                y="Salary", 
                title="Age/Salary Distribution"
            )


def selection():
    return pc.vstack(
        pc.hstack(
            pc.vstack(
                pc.select(
                    ["C", "PF", "SF", "PG", "SG"],
                    placeholder="Select a position. (All)",
                    on_change=State.set_position,
                ),
                pc.select(
                    college,
                    placeholder="Select a college. (All)",
                    on_change=State.set_college,
                ),
            ),
            pc.vstack(
                pc.vstack(
                    pc.hstack(
                        pc.badge("Min Age: ", State.age[0]),
                        pc.spacer(),
                        pc.badge("Max Age: ", State.age[1]),
                    ),
                    pc.range_slider(on_change_end=State.set_age, min_=18, max_=50),
                    align_items="left",
                    width="100%",
                ),
                pc.vstack(
                    pc.hstack(
                        pc.badge("Min Sal: ", State.salary[0] // 1000000, "M"),
                        pc.spacer(),
                        pc.badge("Max Sal: ", State.salary[1] // 1000000, "M"),
                    ),
                    pc.range_slider(
                        on_change_end=State.set_salary, min_=0, max_=25000000
                    ),
                    align_items="left",
                    width="100%",
                ),
            ),
            spacing="1em",
        ),
        width="100%",
    )


def index():
    return pc.center(
        pc.vstack(
            navbar(),
            selection(),
            pc.divider(),
            pc.plotly(data=State.scat_fig, layout={"width": "1000", "height": "600"}),
            pc.plotly(data=State.hist_fig, layout={"width": "1000", "height": "600"}),
            pc.data_table(
                data=nba_data.to_pandas(),
                pagination=True,
                search=True,
                sort=True,
                resizable=True,
            )
        ),

        padding_top="10%",
    )

def topics():
    return pc.center(
        pc.vstack(
            navbar(),
            selection(),
            pc.divider(),
            pc.hstack(
                pc.button(
                    "Decrement",
                    color_scheme="red",
                    border_radius="1em",
                    on_click=State.decrement,
                ),
                pc.heading(State.count, font_size="2em"),
                pc.button(
                    "Increment",
                    color_scheme="green",
                    border_radius="1em",
                    on_click=State.increment,
                ),
            ),
        ),
        padding_top="10%",
    )


def about():
    return pc.text("About Page")


def custom():
    return pc.text("Custom Route")


app = pc.App(state=State)

app.add_page(index, title="Test JSR")
app.add_page(topics)
app.add_page(about)
app.add_page(custom)

app.compile()
