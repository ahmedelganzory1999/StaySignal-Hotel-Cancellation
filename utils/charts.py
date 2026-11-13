import plotly.express as px
import plotly.graph_objects as go

LIME = "#C9FC62"
CORAL = "#FF8471"
MINT = "#80D4B8"
BLUE = "#79BDF5"
PAPER = "#EFF3EB"
MUTED = "#A8B6AD"
PALETTE = [LIME, CORAL, BLUE, MINT, "#F3CD83", "#BFA4F7"]


def finish(fig, height=400, percent=False):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=14, t=56, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, Arial, sans-serif", color=PAPER, size=13),
        title=dict(font=dict(family="Fraunces, Georgia, serif", size=23, color=PAPER), x=0),
        hoverlabel=dict(bgcolor="#151E1A", font_color=PAPER),
        legend=dict(bgcolor="rgba(0,0,0,0)", title_text=""),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(237,244,232,.18)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(237,244,232,.08)", zeroline=False)
    if percent:
        fig.update_yaxes(ticksuffix="%")
    return fig


def bar(df, x, y, title, *, horizontal=False, colors=None, height=400, percent=False, text=None):
    colors = colors or [LIME]
    fig = px.bar(
        df, x=y if horizontal else x, y=x if horizontal else y,
        orientation="h" if horizontal else "v", color_discrete_sequence=colors,
        text=text, title=title,
    )
    fig.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False)
    return finish(fig, height=height, percent=percent)


def line(df, x, y, title, *, color=None, height=400):
    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title,
                  color_discrete_sequence=PALETTE)
    fig.update_traces(line_width=3, marker_size=8)
    return finish(fig, height=height)


def donut(df, names, values, title):
    fig = px.pie(df, names=names, values=values, hole=.7, title=title,
                 color_discrete_sequence=[LIME, CORAL, BLUE, MINT])
    fig.update_traces(textposition="outside", textinfo="percent+label")
    return finish(fig, height=390)
