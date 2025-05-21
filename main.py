from sklearn.datasets import load_iris
from utils import func_dash_app_del_column
import streamlit as st

iris = load_iris(as_frame=True).frame
iris["species"] = iris["target"].map(dict(enumerate(load_iris().target_names)))

st.set_page_config(layout="wide")
st.title("🧪 Streamlit + Dash Table App")

# Example with all features enabled:
func_dash_app_del_column(iris, port=8056, col_delete=True, add_row=True)
