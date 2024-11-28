import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from millify import millify
import plotly.graph_objects as go
import numpy as np
import matplotlib.cm as cm
import time 
import pandas as pd

# --------------------------------------------------------------------------------------------------

tabs = st.tabs(['Snapshot', 'KPIs'])

with tabs[0]:

    cols = st.columns([1, 2, 1])
    with cols[0]:
        button1 = st.button(f"""**{st.session_state.analysis['num_publishers']:,}**
        \nData Providers
        """)
        button2 = st.button(f"""**{st.session_state.analysis['num_feeds']:,}**
        \nData feeds
        """)
        button3 = st.button(f"""**{st.session_state.analysis['total_num_activities']:,}**
        \nActivities and facilities
        """)
        opps = millify(st.session_state.analysis['total_num_opportunities'], precision=1)
        button4 = st.button(f"""**{opps}** 
        \nLive opportunities
        """)
    with cols[1]:
        content = st.empty()
        if button1 or (not (button1 or button2 or button3 or button4)):
            content.empty()
            st.markdown("**OpenActive** is a decentralised open data initiative. Each data provider shares one or more data feeds, providing near real time availability of their activities and facilities.")   
            st.markdown(" ")
            st.markdown("""The <a href="https://status.openactive.io/" target="_blank"><b>status page</b></a> lists the data providers and basic information about the status of each feed.""", unsafe_allow_html=True)
            st.markdown(" ")
            st.markdown("Some data providers are National Governing Bodies, some are big leisure providers, while others create systems to allow smaller activity providers to open their data.")
            st.markdown(" ")
            orgs = len(st.session_state.analysis['df_total_organisers_counts'])
            st.markdown(f"This snapshot of the data contains activities and facilities from **{orgs}** different providers.")
            st.divider()
            image_placeholder = st.empty()  # Placeholder for all images
            num_images_to_show = 6 
            for i in range(len(st.session_state.logo_urls)):
                with image_placeholder.container():  # Use the container
                    start_index = i % len(st.session_state.logo_urls)
                    image_urls = st.session_state.logo_urls[start_index:min(len(st.session_state.logo_urls), start_index + num_images_to_show)]
                    cols = st.columns(len(image_urls))
                    for j, url in enumerate(image_urls):
                        with cols[j]:
                            st.image(url, width=200)
                time.sleep(0.7)
                image_placeholder.empty() # Clear the entire placeholder
                
        elif button2:
            content.empty()
            cols = st.columns([1, 2, 1])
            with cols[0]:
                st.markdown("There are different kinds of **OpenActive** data feeds. ")
                st.markdown("Some are designed to be read together, for example:")
                st.markdown(" - A Session Series feed includes details that apply to a number of events: location, activity, organiser, etc")
                st.markdown(" - A Scheduled Session feed includes details that apply to a specific event: date, time, number of spaces remaining, etc")
                
            with cols[1]:
                # Get the data for the donut plot
                df = st.session_state.analysis['df_total_types_counts']

                # Group categories less than 1% for the donut plot
                df_donut = df.copy()  # Create a copy to avoid modifying the original DataFrame
                df_donut['type'] = df_donut.apply(lambda row: row['type'] if row['percentage'] >= 1 else 'Other', axis=1)
                df_donut = df_donut.groupby('type').sum().reset_index()

                labels = df_donut['type'].tolist()
                values = df_donut['percentage'].tolist()

                # Create the donut plot using Plotly
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5)])
                fig.update_layout(
                    title="OpenActive Opportunity Types",
                    width=600,
                    height=400,
                    margin=dict(l=0, r=0, t=50, b=0),
                    showlegend=True,
                )
                st.plotly_chart(fig, use_container_width=True)

            # Display the table with original 'type' values
            st.dataframe(df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'type': 'OA type',
                    'count': 'Num. opportunities',
                    'percentage': st.column_config.NumberColumn(
                    '% opportunities',
                    format='%0.1f',),
                },
                )
            st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_types']:,}")

        elif button3:
            content.empty()
            st.markdown("The official OpenActive activity list contains over 700 standardised activity names, though publishers can and do use their own wording for activity and facility labels.")
            st.dataframe(
                st.session_state.analysis['df_total_activities_counts'],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'activity': 'OA activity',
                    'count': 'Num. opportunities',
                    'percentage': st.column_config.NumberColumn(
                        '% opportunities',
                        format='%0.1f',
                    ),
                },
            )
            st.write(f"Num. activities: {st.session_state.analysis['total_num_activities']:,}")
            st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_activities']:,}")
        elif button4:
            content.empty()
            cols = st.columns([1, 2, 1])
            with cols[0]:
                st.markdown("OpenActive describes standards to make sharing information about 'opportunities for sport and physical activity' easier and more effective. We use the word 'opportunity' to describe the individual items or records that are contained in data feeds. Because the feeds vary in level of detail they represent, the total 'opportunity' count is quite a crude measure. But generally, an increase in total opportunities shows that more activity and facility data is being made open, and we think that is a good thing!")
                st.markdown(" ")
                st.markdown(f"These figures include data from {st.session_state.analysis['num_feeds_preview']} preview feeds with {millify(st.session_state.analysis['total_num_opportunities_preview'], precision=1)} preview opportunities.")
                st.markdown(f'This snapshot of the OpenActive ecosystem was created on {datetime.now().date()}.')                       
            with cols[1]:
                fig, ax = plt.subplots(1, 1, figsize=(3, 6))
                plt.style.use('ggplot')
                st.session_state.analysis['gdf_total_regions_counts'].plot(
                    column='percentage',
                    # cmap='YlOrRd',
                    cmap='inferno_r',
                    ax=ax,
                )
                ax.set(facecolor='white')
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title('% of OpenActive Opportunities by Region')
                scalarmappable = ax.collections[0] # Assuming there's only one collection in the plot
                colorbar = plt.colorbar(scalarmappable,  orientation='horizontal', pad=-0.04)
                colorbar.set_label('%')
                st.pyplot(fig)
                plt.close(fig)

# dated_counts = {
#     'Jan 17': 0,
#     'Jul 17': 80000,
#     'Jan 18': 80000,
#     'Jul 18': 110000,
#     'Jan 19': 160000,
#     'Jun 19': 200000,
# }

# current_month = datetime.now().strftime('%b %y')
# dated_counts[current_month] = st.session_state.analysis['total_num_opportunities']
# df = pd.DataFrame.from_dict(dated_counts, orient='index', columns=['Count'])
# df.reset_index(inplace=True)
# df.columns = ['Date', 'Count']
# df['Date'] = pd.to_datetime(df['Date'], format='%b %y')
# df = df.sort_values(by='Date')

# st.line_chart(df, x='Date', y='Count')

with tabs[1]:
        st.header('Key Performance Indicators')

        st.subheader('Growth of OpenActive')
        st.subheader(f"{st.session_state.analysis['percentage_sad_matched']:.1f}% of Sport England recognised Sports and Disciplines appear in OpenActive data feeds")
        with st.expander('A higher value means more of the sports and disciplines recognised by Sport England are discoverable through the OpenActive ecosystem. Click here for more details.'):
            cols = st.columns([2, 1])
            with cols[0]:
                st.write(f"Matched SE categories: {st.session_state.analysis['num_sad_matched']} / {st.session_state.analysis['num_sad']} ({st.session_state.analysis['percentage_sad_matched']:.1f}%)")
                st.dataframe(
                    st.session_state.analysis['df_total_sad_counts_matched'],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'sport_and_discipline': 'SE sport and discipline',
                        'activity': st.column_config.TextColumn(
                            'OA activity',
                            width='small',
                        ),
                        'count_activities': 'Num. activities',
                        'count_opportunities': 'Num. opportunities',
                        'percentage_activities': st.column_config.NumberColumn(
                            '% activities',
                            format='%0.1f',
                        ),
                        'percentage_opportunities': st.column_config.NumberColumn(
                            '% opportunities',
                            format='%0.1f',
                        ),
                    },
                )
                st.write(f"Num. activities: {st.session_state.analysis['total_num_activities_with_sad']:,}")
                st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_sad']:,}")
            with cols[1]:
                st.write(f"Unmatched SE categories: {st.session_state.analysis['num_sad_unmatched']} / {st.session_state.analysis['num_sad']} ({st.session_state.analysis['percentage_sad_unmatched']:.1f}%)")
                st.dataframe(
                    st.session_state.analysis['df_se_sport_and_discipline_unmatched'][['sport', 'discipline']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'sport': 'SE sport',
                        'discipline': 'SE discipline',
                    }
                )

            st.divider()

            st.write('Activities - Activities featured as individual concepts in the [OpenActive Activity List](https://activity-list.openactive.io/en/hierarchical_concepts.html).')
            st.write('Sports - Sports featured in the list of national governing bodies recognised by the UK Sports Councils. Taken in spreadsheet format from the [Sport England website](https://www.sportengland.org/guidance-and-support/national-governing-bodies?section=recognised_ngbs) and last accessed on 2024-01-24.')
            st.write('Disciplines - Disciplines featured within each of the recognised sports. For example: "crown", "federation", and "short mat" are all distinct disciplines of bowls.')

        st.divider()
        

        gdf = st.session_state.analysis['gdf_total_lads_counts']

        # Filter for counts 50 or greater (important to include NaNs as 'not greater than or equal to 50')
        gdf_filtered = gdf[(gdf['count'] >= 100) | (gdf['count'].isna())]

        # Calculate the percentage
        percentage_100_or_more = (len(gdf_filtered) / len(gdf)) * 100

        st.subheader(f"{percentage_100_or_more:.1f}% of UK Local Authorities have more than 100 opportunities in OpenActive data feeds")
        with st.expander('A higher value means more of the sports and disciplines recognised by Sport England are discoverable through the OpenActive ecosystem. Click here for more details.'):
            cols = st.columns(3)
            with cols[0]:
                st.dataframe(
                    st.session_state.analysis['gdf_total_lads_counts'][['LAD24NM', 'count', 'percentage']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'LAD24NM': 'Location',
                        'count': 'Num. opportunities',
                        'percentage': st.column_config.NumberColumn(
                            '% opportunities',
                            format='%0.1f',
                        ),
                    },
                )
                st.write(f"Num. locations: {st.session_state.analysis['total_num_lads']:,}")
                st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_lads']:,}")
            with cols[1]:
                fig, ax = plt.subplots(1, 1, figsize=(8, 8))
                st.session_state.analysis['gdf_total_lads_counts'].plot(
                    column='percentage',
                    # cmap='YlOrRd',
                    cmap='inferno_r',
                    legend=True,
                    ax=ax,
                )
                ax.set(facecolor='white')
                ax.set_xticks([])
                ax.set_yticks([])
                st.pyplot(fig)
                plt.close(fig)

                st.divider()
                # Sample data provided (replace with your actual data loading)
                data = """0,	945,	3285
                1,	1037,	3284
                2,	1189,	3284
                3,	1289,	3285
                4,	1360,	3284
                5,	1451,	3284
                6,	1478,	3285
                7,	1557,	3284
                8,	1504,	3284
                9,	1560,	3285"""

                # Convert the string data to DataFrame
                from io import StringIO  # For string data
                df = pd.read_csv(StringIO(data), header=None, names=['decile', 'LSOA count', 'LSOA total count'])

                # Calculate percentage
                df['percentage'] = (df['LSOA count'] / df['LSOA total count']) * 100

                # Create horizontal bar chart using Plotly
                fig = go.Figure(go.Bar(
                    y=df['decile'],  # Decile on the y-axis (vertical)
                    x=df['percentage'],  # Percentage on the x-axis (horizontal)
                    orientation='h',  # Horizontal orientation
                    marker_color='#e11482', # OpenActive pink.
                ))

                fig.update_layout(
                    title="Percentage of OA coverage at LSOA area, by deprivation index",
                    xaxis_title="Percentage",
                    yaxis_title="Decile",
                    height=600,  # Adjust height as needed
                    xaxis_range=[0, 100] # Set x-axis range from 0 to 100
                )

                # Display chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)

                st.write('Activities - Activities featured as individual concepts in the [OpenActive Activity List](https://activity-list.openactive.io/en/hierarchical_concepts.html).')
                st.write('Sports - Sports featured in the list of national governing bodies recognised by the UK Sports Councils. Taken in spreadsheet format from the [Sport England website](https://www.sportengland.org/guidance-and-support/national-governing-bodies?section=recognised_ngbs) and last accessed on 2024-01-24.')
                st.write('Disciplines - Disciplines featured within each of the recognised sports. For example: "crown", "federation", and "short mat" are all distinct disciplines of bowls.')

print(st.session_state.analysis.keys())
print(st.session_state.analysis['total_num_lads'])
print(st.session_state.analysis['gdf_total_lads_counts'])
        
#  Alternatively, to explicitly handle NaNs:
#count_less_than_50 = gdf[ (gdf['count'] < 50) | (gdf['count'].isna()) ].shape[0]

#print(f"Number of rows with count less than 10: {count_less_than_50}") 

# Filter rows where 'count' is less than 10, including NaNs
#gdf_filtered = gdf[ (gdf['count'] < 50) | (gdf['count'].isna()) ][['LAD24NM', 'count']]

#st.dataframe(gdf_filtered,
#    use_container_width=True,
#    hide_index=True,
#    column_config={
#        "LAD24NM": "Location",
#        "count": "Opportunity Count",  # More descriptive column name
#    })         
    