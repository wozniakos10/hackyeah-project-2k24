# Slightly modified copy of the: https://github.com/REPNOT/streamviz
from typing import Any

import plotly.graph_objects as go
import streamlit as st


def gauge(
    gVal: Any,
    gTitle: str = "",
    gMode: str = "gauge+number",
    gSize: str = "FULL",
    gTheme: str = "Black",
    grLow: float = 0.29,
    grMid: float = 0.69,
    gcLow: str = "#FF1708",
    gcMid: str = "#FF9400",
    gcHigh: str = "#1B8720",
    xpLeft: int = 0,
    xpRight: int = 1,
    ypBot: int = 0,
    ypTop: int = 1,
    arBot: float | None = None,
    arTop: float = 1,
    pTheme: str = "streamlit",
    cWidth: bool = True,
    sFix: str | None = None,
) -> None:
    """Deploy Plotly gauge or indicator data visualization

    Keyword arguments:

    gVal -- gauge Value (required)
        Description:
            The value passed to this argument is displayed in
            the center of the visualization, drives the color & position
            of the gauge and is required to successfully call this function.
        Data Type:
            integer, float

    gTitle -- gauge Title (default '')
        Description:
            Adds a header displayed at the top
            of the visualization.
        Data Type:
            string

    gMode -- gauge Mode (default gauge+number)
        Description:
            Declares which type of visualization should
            be displayed.
        Options:
            gauge+number, gauge, number
        Data Type:
            string

    gSize -- gauge Size (default FULL)
        Description:
            Automatically resizes the gauge or indicator using
            pre-defined values options.

            The size of visualization can also be customized by passing the 'CUST' value to
            the argument and assigning a decimal value from 0 to 1 to the following
            arguments; xpLeft, xpRight, ypBot, and ypTop.
        Options:
            SML, MED, LRG, FULL, CUST
        Data Type:
            String

    grLow -- Low gauge Range (default 0.30)
        Description:
            Sets the bottom (lowest) percentile target group for the gauge value.
            When the gauge Value (gVal) is less than the value assigned to this
            argument, the color assigned to the gcLow (Low gauge Color) argument
            is displayed.
        Data Type:
            integer, float

    grMid -- Middle gauge Range (default 0.70)
        Description:
            Sets the middle percentile target group for the gauge value.  When
            the gauge Value (gVal) is less than the value assigned to this argument,
            the color assigned to the gcMid (Middle gauge Color) argument is displayed.

            If the value assigned to the gVal argument is greater than or equal to
            the value assigned to the grMid argument, the color value assigned to
            gcHigh will then be displayed.
        Data Type:
            integer, float

    gcLow -- Low gauge Color (default #FF1708)
        Description:
            gauge color for bottom percentile target group. Default value
            is a hex code for red.  Argument excepts hex color codes and
            there associated names.
        Data Type:
            string

    gcMid -- Middle gauge Color (default #FF9400)
        Description:
            gauge color for middle percentile target group. Default value
            is a hex code for orange.  Argument excepts hex color codes and
            there associated names.
        Data Type:
            string

    gcHigh -- High gauge Color (default #1B8720)
        Description:
            gauge color for middle percentile target group. Default value
            is a hex code for green.  Argument excepts hex color codes and
            there associated names.
        Data Type:
            string

    sFix -- gauge Value Suffix (default 0.0)
        Description:
            Adds a suffix (character) to the gauge value displayed in the
            center of the visualization.

            Assigning the '%' character to this argument will display the
            percentage symbol at the end of the value shown in the center
            of the visualization and convert the gauge value from a floating
            point integer so the value displays correctly as a percentage.
        Options:
            %
        Data Type:
            string

    xpLeft -- X-Axis Position 1 for Plot (default 0.0)
    xpRight --  X-Axis Position 2 for Plot (default 0.0)
    ypBot --  X-Axis Position 1 for Plot (default 0.0)
    ypTop --  X-Axis Position 2 for Plot (default 0.0)
    arBot -- Bottom Axis Range Value (default 0.0)
    arTop --  Bottom Axis Range Value (default 0.0)
    pTheme -- Plot Theme (default 0.0)
    cWidth -- Container Width (default 0.0)
    """

    if sFix == "%":
        gaugeVal = round((gVal * 100), 1)
        top_axis_range = arTop * 100
        bottom_axis_range = arBot
        low_gauge_range = grLow * 100
        mid_gauge_range = grMid * 100

    else:
        gaugeVal = gVal
        top_axis_range = arTop
        bottom_axis_range = arBot
        low_gauge_range = grLow
        mid_gauge_range = grMid

    if gSize == "SML":
        x1, x2, y1, y2 = 0.25, 0.25, 0.75, 1
    elif gSize == "MED":
        x1, x2, y1, y2 = 0.50, 0.50, 0.50, 1
    elif gSize == "LRG":
        x1, x2, y1, y2 = 0.75, 0.75, 0.25, 1
    elif gSize == "FULL":
        x1, x2, y1, y2 = 0, 1, 0, 1
    elif gSize == "CUST":
        x1, x2, y1, y2 = xpLeft, xpRight, ypBot, ypTop

    if gaugeVal <= low_gauge_range:
        gaugeColor = gcLow
    elif gaugeVal >= low_gauge_range and gaugeVal <= mid_gauge_range:
        gaugeColor = gcMid
    else:
        gaugeColor = gcHigh

    fig1 = go.Figure(
        go.Indicator(
            mode=gMode,
            value=gaugeVal,
            domain={"x": [x1, x2], "y": [y1, y2]},
            number={"suffix": sFix},
            title={"text": gTitle},
            gauge={"axis": {"range": [bottom_axis_range, top_axis_range]}, "bar": {"color": gaugeColor}},
        )
    )

    config = {"displayModeBar": False}
    fig1.update_traces(title_font_color=gTheme, selector=dict(type="indicator"))
    fig1.update_traces(number_font_color=gTheme, selector=dict(type="indicator"))
    fig1.update_traces(gauge_axis_tickfont_color=gTheme, selector=dict(type="indicator"))
    fig1.update_layout(margin_l=20)
    fig1.update_layout(margin_r=20)
    fig1.update_layout(margin=dict(t=50, b=0), height=150)

    fig1.update_layout(margin_autoexpand=False)

    st.plotly_chart(fig1, use_container_width=cWidth, theme=pTheme, **{"config": config})
