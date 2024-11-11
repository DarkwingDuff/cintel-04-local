from shiny.express import input, ui
from shinywidgets import render_plotly
from shiny.express import output, render, ui
from shiny.express import input, ui, render
from palmerpenguins import load_penguins
from shinywidgets import output_widget, render_widget
import seaborn as sns
import matplotlib.pyplot as plt
import palmerpenguins
import plotly.express as px
from io import BytesIO
from shiny import render
from shinywidgets import output_widget, render_widget, render_plotly
from shiny import reactive
import base64

penguins_df = palmerpenguins.load_penguins()
print(penguins_df)

data = penguins_df

ui.page_opts(title="Penguin ", fillable=True, class_="scrollable")
ui.tags.style(":root { --bs-primary-rgb: 113,46,246; }")

with ui.sidebar(open="open"):
    ui.h2("Sidebar")
    ui.input_selectize(
        "selected_attribute",
        "Penguin Metric",
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    )
    ui.input_numeric("plotly_bin_count", "Number of Bins", 50)
    ui.input_slider("seaborn_bin_count", "Seaborn Bins", 0, 100, 50)
    ui.input_checkbox_group(
        "Selected_Species_List",
        "Species Selection",
        ["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
        inline=False,
    )
    ui.hr()
    ui.a(
        "Github",
        href="https://github.com/DarkwingDuff/cintel-02-data/tree/main",
        target="_blank",
    )


# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

# Add a reactive calculation to filter the data
# By decorating the function with @reactive, we can use the function to filter the data
# The function will be called whenever an input functions used to generate that output changes.
# Any output that depends on the reactive function (e.g., filtered_data()) will be updated when the data changes.

with ui.layout_columns():
    with ui.navset_card_tab(id="plot_tabs"):
        with ui.nav_panel("Scatterplot"):

            with ui.card(full_screen=True):

                ui.card_header("Scatterplot: Species", style="color:white; background:#2A2A2A !important;")

                @render_widget
                def scatter_plot():
                    selected_species = input.Selected_Species_List()
                    selected_attribute = input.selected_attribute()
                    filtered_df = penguins_df[
                        penguins_df["species"].isin(selected_species)
                    ]
                    fig = px.scatter(
                        filtered_df,
                        x="bill_length_mm",
                        y="bill_depth_mm",
                        color="species",
                        title="Scatter Plot of Penguin Bill Dimensions",
                    )
                    return fig

        with ui.nav_panel("Density Plot"):
             with ui.card(full_screen=True):

                ui.card_header("Density Plot: Species", style="color:white; background:#3101B7 !important;")
            
                @render_plotly
                def density_plot():
                    filtered_penguins = penguins_df[
                        penguins_df["species"].isin(input.Selected_Species_List())
                    ]
                    fig = px.density_contour(
                        filtered_penguins,
                        x="bill_length_mm",
                        y="flipper_length_mm",
                        color="species",
                        title="Density Plot: Bill Length vs Bill Depth by Species",
                        labels={
                            "bill_length_mm": "Bill Length (mm)",
                            "flipper_length_mm": "Flipper Depth (mm)",
                        },
                    )
                    return fig

        with ui.nav_panel("Tips Histogram"):
            with ui.card(full_screen=True):

                ui.card_header("Tips Histogram", style="color:white; background:#06B22F !important;")

                @render_plotly
                def plot1():
                    return px.histogram(px.data.tips(), y="tip")

        with ui.nav_panel("Bill Histogram"):
                with ui.card(full_screen=True):
                    ui.card_header("Bill Histogram", style="color:white; background:#B3052A !important;")
    
                    @render_plotly
                    def plot2():
                        return px.histogram(px.data.tips(), y="total_bill")

        with ui.nav_panel("Seaborn Histograms"):

            @reactive.calc
            def filtered_data():
                return data

            with ui.layout_columns():
                with ui.card(full_screen=True):
                    ui.card_header("Palmer Penguin Historgram", style="color:Black; background:#D2F61E !important;")
                    @render.plot(
                        alt="A Seaborn histogram on penguin body mass in grams."
                    )
                    def seaborn_histogram1():
                        selected_attribute = input.selected_attribute()
                        bin_count = input.seaborn_bin_count()

                        # Filter the data based on species selection
                        selected_species = input.Selected_Species_List()
                        filtered_df = penguins_df[
                            penguins_df["species"].isin(selected_species)
                        ]
                        histplot = sns.histplot(
                            filtered_df[selected_attribute].dropna(),
                            bins=bin_count,
                            kde=True,
                        )
                        histplot.set_title("Palmer Penguins")
                        histplot.set_xlabel(
                            f"{selected_attribute}, Species:{selected_species}"
                        )
                        histplot.set_ylabel("Count")
                        return histplot

                with ui.card(full_screen=True):
                    ui.card_header("Penguin Historgram", style="color:White; background:#4D9232 !important;")
                    @output
                    @render.ui
                    def seaborn_histogram():
                        # Reactive inputs
                        selected_attribute = input.selected_attribute()
                        bin_count = input.seaborn_bin_count()

                        # Filter the data based on species selection
                        selected_species = input.Selected_Species_List()
                        filtered_df = penguins_df[
                            penguins_df["species"].isin(selected_species)
                        ]

                        # Create the Seaborn histogram plot
                        plt.figure(figsize=(8, 6))
                        sns.histplot(
                            filtered_df[selected_attribute].dropna(),
                            bins=bin_count,
                            kde=True,
                        )
                        plt.xlabel(selected_attribute)
                        plt.title(f"Seaborn Histogram of {selected_attribute}")

                        # Save plot to a bytes buffer and encode as base64
                        buf = BytesIO()
                        plt.savefig(buf, format="png")
                        plt.close()
                        buf.seek(0)
                        image_base64 = base64.b64encode(buf.read()).decode("utf-8")

                        # Return the base64-encoded image as an HTML <img> tag
                        return ui.HTML(
                            f'<img src="data:image/png;base64,{image_base64}" />'
                        )


with ui.layout_columns():
    with ui.card():

        @render.data_frame
        def plot3():
            return render.DataTable(data, selection_mode="row")

    with ui.card():

        @render.data_frame
        def plot4():
            return render.DataGrid(data, selection_mode="row")
