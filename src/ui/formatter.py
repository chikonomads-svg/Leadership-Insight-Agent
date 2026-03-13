import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart(chart_config: dict):
    """
    Renders a dynamic Plotly graph in Streamlit from a given chart configuration dict.
    """
    if not chart_config or not chart_config.get("has_data") or chart_config.get("chart_type") == "none":
        return
        
    data = chart_config.get("data", [])
    if not data:
        return
        
    df = pd.DataFrame(data)
    chart_type = chart_config.get("chart_type")
    title = chart_config.get("title", "")
    x_label = chart_config.get("x_axis_label", "Label")
    y_label = chart_config.get("y_axis_label", "Value")
    
    fig = None
    if chart_type == "bar":
        fig = px.bar(df, x="label", y="value", title=title, labels={"label": x_label, "value": y_label})
    elif chart_type == "line":
        fig = px.line(df, x="label", y="value", title=title, labels={"label": x_label, "value": y_label}, markers=True)
    elif chart_type == "pie":
        fig = px.pie(df, names="label", values="value", title=title)
        
    if fig:
        st.plotly_chart(fig, use_container_width=True)
