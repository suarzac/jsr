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

youtube_overview = "data/USvideos.csv"
youtube_data = pl.read_csv(youtube_overview)
categories = sorted(youtube_data["category_id"].unique().drop_nulls().cast(str))

nba_overview = "https://media.geeksforgeeks.org/wp-content/uploads/nba.csv"
#
nba_data = pl.read_csv(nba_overview)
college = sorted(nba_data["College"].unique().drop_nulls().cast(str))

class baseState(pc.State):
    """The app state."""

    count: int = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1

class youtubeState(baseState):
    # yt
    channelTitle: str
    categoryId: str
    likes: list = [0, 25000000]
    dislikes: list = [0, 25000000]

    @pc.var
    def df(self) -> pl.DataFrame:
        """The data."""

        yt = youtube_data.filter(
            (youtube_data["likes"] > int(self.likes[0]))
            & (youtube_data["likes"] < int(self.likes[1]))
            & (youtube_data["dislikes"] > int(self.dislikes[0]))
            & (youtube_data["dislikes"] < int(self.dislikes[1])) 
        )

        if self.channelTitle and self.channelTitle != "All":
            yt = [yt["channel_title"] == self.channelTitle]

        if self.categoryId and self.categoryId != "All":
            yt = yt[yt["category_id"] == self.categoryId]

        if yt.is_empty():
            return pl.DataFrame()
        else:
            return yt.fill_nan("")

    @pc.var
    def scat_fig(self) -> go.Figure:
        """The scatter figure."""
        yt = self.df

        if yt.is_empty():
            return go.Figure()
        else:
            return px.bar(
                yt.to_pandas(),
                x="channel_title",
                y="likes",
                title="yt Age/Salary plot",
                color=yt["category_id"],
                hover_data=["channel_title"]
            )

    @pc.var
    def hist_fig(self) -> go.Figure:
        """The histogram figure."""
        yt = self.df

        if yt.is_empty():
            return go.Figure()
        else:
            return px.histogram(
                yt.to_pandas(), 
                x="channel_title", 
                y="likes", 
                title="channel title and likes"
            )

class nbaState(baseState):
    """The app state."""

    position: str
    college: str
    age: list = [0, 50]
    salary: list = [0, 25000000]

    @pc.var
    def df(self) -> pl.DataFrame:
        """The data."""

        nba = nba_data.filter(
            (nba_data["Age"] > int(self.age[0]))
            & (nba_data["Age"] < int(self.age[1]))
            & (nba_data["Salary"] > int(self.salary[0]))
            & (nba_data["Salary"] < int(self.salary[1])) 
        )

        if self.college and self.college != "All":
            nba = nba[nba["College"] == self.college]

        if self.position and self.position != "All":
            nba = nba[nba["Position"] == self.position]

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

def youtubeSelection():
    return pc.vstack(
        pc.hstack(
            pc.vstack(
                pc.select(
                    categories,
                    placeholder="Select a category id. (All)",
                    on_change=youtubeState.set_categoryId
                ),
                pc.select(
                    college,
                    placeholder="Select a channel title. (All)",
                    on_change=youtubeState.set_channelTitle,
                ),
            ),
            pc.vstack(
                pc.vstack(
                    pc.hstack(
                        pc.badge("Min likes: ", youtubeState.likes[0]),
                        pc.spacer(),
                        pc.badge("Max likes: ", youtubeState.likes[1]),
                    ),
                    pc.range_slider(on_change_end=youtubeState.set_likes, min_=0, max_=25000000),
                    align_items="left",
                    width="100%",
                ),
                pc.vstack(
                    pc.hstack(
                        pc.badge("Min dislikes: ", youtubeState.dislikes[0], "M"),
                        pc.spacer(),
                        pc.badge("Max dislikes: ", youtubeState.dislikes[1], "M"),
                    ),
                    pc.range_slider(
                        on_change_end=youtubeState.set_dislikes, min_=0, max_=25000000
                    ),
                    align_items="left",
                    width="100%",
                ),
            ),
            spacing="1em",
        ),
        width="100%",
    )

def nbaSelection():
    return pc.vstack(
        pc.hstack(
            pc.vstack(
                pc.select(
                    ["C", "PF", "SF", "PG", "SG"],
                    placeholder="Select a position. (All)",
                    on_change=nbaState.set_position,
                ),
                pc.select(
                    college,
                    placeholder="Select a college. (All)",
                    on_change=nbaState.set_college,
                ),
            ),
            pc.vstack(
                pc.vstack(
                    pc.hstack(
                        pc.badge("Min Age: ", nbaState.age[0]),
                        pc.spacer(),
                        pc.badge("Max Age: ", nbaState.age[1]),
                    ),
                    pc.range_slider(on_change_end=nbaState.set_age, min_=18, max_=50),
                    align_items="left",
                    width="100%",
                ),
                pc.vstack(
                    pc.hstack(
                        pc.badge("Min Sal: ", nbaState.salary[0] // 1000000, "M"),
                        pc.spacer(),
                        pc.badge("Max Sal: ", nbaState.salary[1] // 1000000, "M"),
                    ),
                    pc.range_slider(
                        on_change_end=nbaState.set_salary, min_=0, max_=25000000
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
            nbaSelection(),
            pc.divider(),
            pc.plotly(data=nbaState.scat_fig, layout={"width": "1000", "height": "600"}),
            pc.plotly(data=nbaState.hist_fig, layout={"width": "1000", "height": "600"}),
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


def about():
    return pc.center(
        pc.vstack(
            navbar(),
            youtubeSelection(),
            pc.divider(),
            pc.plotly(data=youtubeState.scat_fig, layout={"width": "1000", "height": "600"}),
            pc.plotly(data=youtubeState.hist_fig, layout={"width": "1000", "height": "600"}),
            pc.data_table(
                data=youtube_data.to_pandas(),
                pagination=True,
                search=True,
                sort=True,
                resizable=True,
            )
        ),

        padding_top="10%",
    )


def custom():
    return pc.text("Custom Route")


app = pc.App(state=baseState)

app.add_page(index, title="Test JSR")
app.add_page(topics)
# app.add_page(about)
app.add_page(custom)

app.compile()
