def func_dash_app_del_column(df, port=8050, col_delete=True, add_row=False):
    import pandas as pd
    import os
    import threading
    from dash import Dash, dash_table, html, Input, Output, State
    import streamlit as st
    import streamlit.components.v1 as components

    FILTERED_FILE = "filtered_output_df.csv"

    # ----------------------------
    # DASH APP
    # ----------------------------
    def run_dash(df):
        app = Dash(__name__)
        app.title = "Editable Dash Table"

        app.layout = html.Div([
            dash_table.DataTable(
                id="editable-table",
                columns=[
                    {
                        "name": col,
                        "id": col,
                        "deletable": col_delete,
                        "renamable": True,
                        "hideable": True
                    }
                    for col in df.columns
                ],
                data=df.to_dict("records"),
                editable=True,
                row_deletable=True,
                style_table={
                    "overflowX": "auto",
                    "maxHeight": "500px",
                    "minWidth": "100%",
                    "border": "1px solid lightgrey"
                },
                style_cell={
                    "minWidth": "120px",
                    "width": "150px",
                    "maxWidth": "200px",
                    "textAlign": "center"
                }
            ),
            html.Br(),
            html.Div(
                children=[
                    html.Button("➕ Add Row", id="add-row-btn", n_clicks=0,
                                style={"marginRight": "15px", "padding": "10px", "fontSize": "16px"})
                    if add_row else None,
                    html.Button("✅ Save Table", id="save-btn", n_clicks=0,
                                style={"padding": "10px", "fontSize": "16px"})
                ],
                style={"display": "flex", "flexWrap": "wrap"}
            ),
            html.Div(id="save-status", style={"marginTop": "10px"})
        ], style={"padding": "30px"})

        # Add Row logic (only defined if enabled)
        if add_row:
            @app.callback(
                Output("editable-table", "data"),
                Input("add-row-btn", "n_clicks"),
                State("editable-table", "data"),
                State("editable-table", "columns"),
                prevent_initial_call=True
            )
            def add_row_func(n_clicks, data, columns):
                if n_clicks > 0:
                    new_row = {col["id"]: "" for col in columns}
                    return data + [new_row]
                return data

        # Save Table
        @app.callback(
            Output("save-status", "children"),
            Input("save-btn", "n_clicks"),
            State("editable-table", "data"),
            State("editable-table", "columns")
        )
        def save_table(n_clicks, data, columns):
            if n_clicks > 0:
                try:
                    visible_cols = [col["id"] for col in columns]
                    filtered_df = pd.DataFrame(data)[visible_cols]
                    filtered_df.to_csv(FILTERED_FILE, index=False)
                    print("✅ Saved:", visible_cols)
                    return f"✅ Saved {len(visible_cols)} columns"
                except Exception as e:
                    return f"❌ Error: {e}"
            return ""

        app.run_server(debug=False, port=port, use_reloader=False)

    # ----------------------------
    # Start Dash in background thread
    # ----------------------------
    threading.Thread(target=run_dash, args=(df,), daemon=True).start()

    # ----------------------------
    # STREAMLIT UI
    # ----------------------------
    components.iframe(f"http://localhost:{port}", height=900, scrolling=True)

    if st.button("📥 Load Filtered Table"):
        if os.path.exists(FILTERED_FILE):
            try:
                filtered_df = pd.read_csv(FILTERED_FILE)
                st.success(f"✅ Loaded {filtered_df.shape[0]} rows × {filtered_df.shape[1]} columns")
                st.dataframe(filtered_df, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
        else:
            st.warning("⚠️ No saved file found. Click 'Save Table' in Dash.")
