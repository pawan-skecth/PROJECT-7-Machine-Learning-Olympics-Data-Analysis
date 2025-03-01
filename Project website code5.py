pip install gradio

import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.figure_factory as ff


# --- App 1 Functions and UI ---
def display_statistics():
    return f"""
    **Athletes**: {df['Name'].nunique()}
    **Events**: {df['Event'].nunique()}
    **Nations**: {df['region'].nunique()}
    **Sports**: {df['Sport'].nunique()}
    **Editions**: {df['Year'].nunique()}
    """

def medal_tally(year, country):
    temp_df = df.copy()
    if year != "Overall":
        temp_df = temp_df[temp_df["Year"] == int(year)]
    if country != "Overall":
        temp_df = temp_df[temp_df["region"] == country]
    medal_count = temp_df.groupby("region")[["Gold", "Silver", "Bronze"]].sum().reset_index()
    medal_count["Total"] = medal_count["Gold"] + medal_count["Silver"] + medal_count["Bronze"]
    return medal_count if not medal_count.empty else "No Data Available"

def plot_nations_over_time():
    nations = df.drop_duplicates(["Year", "region"]).groupby("Year")["region"].nunique().reset_index()
    return px.line(nations, x="Year", y="region", title="Participating Nations Over the Years")

def plot_events_over_time():
    events = df.drop_duplicates(["Year", "Event"]).groupby("Year")["Event"].nunique().reset_index()
    return px.line(events, x="Year", y="Event", title="Events Over the Years")

def plot_athletes_over_time():
    athletes = df.drop_duplicates(["Year", "Name"]).groupby("Year")["Name"].nunique().reset_index()
    return px.line(athletes, x="Year", y="Name", title="Athletes Over the Years")

def plot_country_medal_tally(country):
    temp_df = df[df["region"] == country].groupby("Year")[["Gold", "Silver", "Bronze"]].sum().reset_index()
    temp_df["Total"] = temp_df["Gold"] + temp_df["Silver"] + temp_df["Bronze"]
    return px.line(temp_df, x="Year", y="Total", title=f"{country} Medal Tally Over the Years") if not temp_df.empty else "No Data Available"

def plot_country_heatmap(country):
    temp_df = df[df['region'] == country].pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    if temp_df.empty:
        return "No Data Available"
    plt.figure(figsize=(12, 8))
    sns.heatmap(temp_df, annot=True, cmap="coolwarm", fmt=".0f")
    plt.title(f"{country} Excels in the Following Sports")
    heatmap_path = "heatmap.png"
    plt.savefig(heatmap_path, bbox_inches="tight")
    plt.close()
    return heatmap_path

def plot_age_distribution():
    athlete_df_local = df.drop_duplicates(subset=['Name', 'region'])
    x1 = athlete_df_local['Age'].dropna().tolist()
    x2 = athlete_df_local[athlete_df_local['Medal'] == 'Gold']['Age'].dropna().tolist()
    x3 = athlete_df_local[athlete_df_local['Medal'] == 'Silver']['Age'].dropna().tolist()
    x4 = athlete_df_local[athlete_df_local['Medal'] == 'Bronze']['Age'].dropna().tolist()
    if not x1:
        return "No Data Available"
    return ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'], show_hist=False)

def most_successful(sport):
    temp_df = df[(df['Sport'] == sport) & (df['Medal'].notna())]
    top_athletes = temp_df['Name'].value_counts().reset_index().head(10)
    top_athletes.columns = ['Name', 'Total Medals']
    return top_athletes.merge(df[['Name', 'Sport', 'region']], on='Name', how='left').drop_duplicates()

def most_successful_country(country):
    temp_df = df[(df['region'] == country) & (df['Medal'].notna())]
    top_athletes = temp_df['Name'].value_counts().reset_index().head(10)
    top_athletes.columns = ['Name', 'Total Medals']
    return top_athletes.merge(df[['Name', 'Sport']], on='Name', how='left').drop_duplicates()

years = ["Overall"] + sorted(df["Year"].unique().tolist())
countries = ["Overall"] + sorted(df["region"].dropna().unique().tolist())
sports = sorted(df['Sport'].dropna().unique().tolist())

# --- App 2 Functions and UI ---
sports_list = sorted(athlete_df[athlete_df['Medal'] == 'Gold']['Sport'].unique())
def plot_age_distribution_sport(sport):
    temp_df = athlete_df[(athlete_df['Sport'] == sport) & (athlete_df['Medal'] == 'Gold')]
    ages = temp_df['Age'].dropna().tolist()
    if not ages:
        return "No data available for this sport."
    fig = ff.create_distplot([ages], [sport], show_hist=False, show_rug=False)
    fig.update_layout(autosize=True, width=900, height=500, title=f"Age Distribution for {sport} (Gold Medalists)")
    return fig

# --- App 3 Functions and UI ---
def plot_gender_participation():
    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()
    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
    final.fillna(0, inplace=True)
    fig = px.line(final, x='Year', y=['Male', 'Female'], title="Men and Women Participation Over the Years")
    return fig

# --- Integrated App ---
with gr.Blocks() as app:
    gr.Markdown("<h1 style='text-align: center; color: blue;'>🏅 Olympic Data Analysis 🏅</h1>")
    with gr.Tab("Main Analysis"):
        gr.Markdown("<h2 style='color: green; font-size: 22px;'>📊 Top Statistics</h2>")
        gr.Textbox(value=display_statistics(), interactive=False)
        gr.Markdown("<h2 style='color: darkred; font-size: 22px;'>🥇 Medal Tally</h2>")
        year_select = gr.Dropdown(choices=years, label="Select Year", value="Overall")
        country_select = gr.Dropdown(choices=countries, label="Select Country", value="Overall")
        medal_output = gr.Dataframe()
        year_select.change(fn=medal_tally, inputs=[year_select, country_select], outputs=medal_output)
        country_select.change(fn=medal_tally, inputs=[year_select, country_select], outputs=medal_output)
        gr.Markdown("<h2 style='font-size: 22px;'>🌍 Participating Nations Over the Years</h2>")
        gr.Plot(value=plot_nations_over_time())
        gr.Markdown("<h2 style='font-size: 22px;'>🏅 Events Over the Years</h2>")
        gr.Plot(value=plot_events_over_time())

        gr.Markdown("<h2 style='font-size: 22px;'>👨‍🎓 Athletes Over the Years</h2>")
        gr.Plot(value=plot_athletes_over_time())

    with gr.Tab("Country Analysis"):
        gr.Markdown("<h2 style='color: darkred; font-size: 22px;'>🌎 Country-wise Medal Tally</h2>")
        country_medal_select = gr.Dropdown(choices=countries, label="Select Country")
        country_medal_output = gr.Plot()
        country_medal_select.change(fn=plot_country_medal_tally, inputs=country_medal_select, outputs=country_medal_output)

        gr.Markdown("<h2 style='color: blue; font-size: 22px;'>🔥 Heatmap of Country Performance</h2>")
        country_heatmap_select = gr.Dropdown(choices=countries, label="Select Country")
        country_heatmap_output = gr.Image()
        country_heatmap_select.change(fn=plot_country_heatmap, inputs=country_heatmap_select, outputs=country_heatmap_output)

    with gr.Tab("Athlete Analysis"):
        gr.Markdown("<h2 style='color: purple; font-size: 22px;'>📈 Age Distribution of Athletes</h2>")
        gr.Plot(value=plot_age_distribution())

        gr.Markdown("<h2 style='color: orange; font-size: 22px;'>🏆 Most Successful Athletes</h2>")
        sport_select = gr.Dropdown(choices=sports, label="Select Sport")
        successful_output = gr.Dataframe()
        sport_select.change(fn=most_successful, inputs=sport_select, outputs=successful_output)

        gr.Markdown("<h2 style='color: green; font-size: 22px;'>🏅 Most Successful Athletes by Country</h2>")
        country_successful_select = gr.Dropdown(choices=countries, label="Select Country")
        country_successful_output = gr.Dataframe()
        country_successful_select.change(fn=most_successful_country, inputs=country_successful_select, outputs=country_successful_output)

    with gr.Tab("Sport Analysis"):
        gr.Markdown("<h2 style='color: red; font-size: 22px;'>📊 Age Distribution in Sports (Gold Medalists)</h2>")
        sport_age_select = gr.Dropdown(choices=sports_list, label="Select Sport")
        sport_age_output = gr.Plot()
        sport_age_select.change(fn=plot_age_distribution_sport, inputs=sport_age_select, outputs=sport_age_output)

    with gr.Tab("Gender Analysis"):
        gr.Markdown("<h2 style='color: blue; font-size: 22px;'>👫 Men vs Women Participation</h2>")
        gr.Plot(value=plot_gender_participation())

app.launch()


import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# Drop missing values for height, weight, and medal
df = df.dropna(subset=["Height", "Weight", "Medal"])

# Convert columns to numeric
df["Height"] = pd.to_numeric(df["Height"], errors="coerce")
df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce")

# Unique sports list
sports_list = sorted(df["Sport"].dropna().unique())

# Function to generate scatter plot
def plot_scatter(sport):
    temp_df = df[df["Sport"] == sport]

    plt.figure(figsize=(10, 6))
    ax = sns.scatterplot(x=temp_df["Weight"], y=temp_df["Height"], hue=temp_df["Medal"], palette="deep")

    plt.xlabel("Weight (kg)")
    plt.ylabel("Height (cm)")
    plt.title(f"Height vs Weight for {sport}")

    # Save the plot
    plot_path = "scatter_plot.png"
    plt.savefig(plot_path, bbox_inches="tight")
    plt.close()

    return plot_path

# Gradio interface
with gr.Blocks() as app:
    gr.Markdown("<h1 style='text-align: center; color: blue;'>🏅 Sports Scatter Plot 🏅</h1>")
    gr.Markdown("<h3 style='text-align: center;'>Select a sport to visualize Height vs Weight of athletes</h3>")

    sport_dropdown = gr.Dropdown(choices=sports_list, label="Select Sport")
    output_plot = gr.Image(label="Scatter Plot")

    sport_dropdown.change(fn=plot_scatter, inputs=sport_dropdown, outputs=output_plot)

# Run the app
app.launch()

