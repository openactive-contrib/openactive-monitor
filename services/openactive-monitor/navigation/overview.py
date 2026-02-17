import leafmap.foliumap as leafmap
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import time
from datetime import date, timedelta
from millify import millify
from streamlit_folium import st_folium
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --------------------------------------------------------------------------------------------------

# Combine SE data for display

# Select desired columns and rename for consistency
matched_df = st.session_state.aggregate_analysis['df_total_sad_counts_matched'][['sport_and_discipline', 'activity', 'percentage_items']].rename(
    columns={'percentage_items': '% of Opportunities'}
)
unmatched_df = st.session_state.aggregate_analysis['df_se_sport_and_discipline_unmatched'][['sport_and_discipline']].rename(
    columns={}
) # Empty dictionary since only one column to select
# Concatenate and sort
combined_SE_df = pd.concat([matched_df, unmatched_df], ignore_index=True).sort_values('sport_and_discipline')

# --------------------------------------------------------------------------------------------------

if ('buttons' not in st.session_state):
    st.session_state.buttons = {
        'providers': f"**{st.session_state.aggregate_analysis['num_publishers']:,}**\n\nData Providers",
        #Note next figure based on feeds.pickle to tally with type counts
        'feeds': f"**{st.session_state.num_feeds:,}**\n\nData feeds",
        'activities': f"**{st.session_state.aggregate_analysis['total_num_activities'] + st.session_state.aggregate_analysis['total_num_facilities']:,}**\n\nActivities and facilities",
        'opportunities': f"**{millify(st.session_state.aggregate_analysis['total_num_future_opportunity_items'], precision=1)}**\n\nLive opportunities",
        'kpis': f"Draft\n\nKPIs"
    }
    st.session_state.button_name_clicked = 'providers'

def click_button(button_name_clicked):
    st.session_state.button_name_clicked = button_name_clicked

# --------------------------------------------------------------------------------------------------

yesterday = date.today() - timedelta(days=1)
st.markdown(
    f'<p style="text-align:right;">OpenActive data as at end of {yesterday}</p>',
    unsafe_allow_html=True
)

cols = st.columns([1, 5])

with cols[0]:
    for button_name, button_text in st.session_state.buttons.items():
        st.button(
            button_text,
            type='primary' if st.session_state.button_name_clicked == button_name else 'secondary',
            on_click=click_button,
            args=[button_name],
        )

with cols[1]:
    content = st.empty()

    if st.session_state.button_name_clicked == 'providers':
        content.empty()
        st.markdown(f"**OpenActive** is a decentralised open data initiative. Each of the **{st.session_state.aggregate_analysis['num_publishers']:,}** data providers shares one or more data feeds, providing near real time availability of their activities and facilities.")
        st.markdown(" ")
        st.markdown("""The <a href="https://status.openactive.io/" target="_blank"><b>status page</b></a> lists the data providers and basic information about the status of each feed.""", unsafe_allow_html=True)
        st.markdown(" ")
        st.markdown("Some data providers are National Governing Bodies, some are big leisure providers, while others create systems to allow smaller activity providers to open their data.")
        st.markdown(" ")
        orgs = len(st.session_state.aggregate_analysis['df_total_organizer_names_counts'])
        st.markdown(f"This snapshot of the data contains activities and facilities from **{orgs:,}** different activity providers.")
        st.divider()

        image_placeholder = st.empty()  # Placeholder for all images
        num_images_to_show = 4
        for i in range(0, len(st.session_state.logo_urls), num_images_to_show):
            with image_placeholder.container():
                image_urls = st.session_state.logo_urls[i:i + num_images_to_show]
                cols = st.columns(num_images_to_show)  # Create columns based on num_images_to_show
                for j, url in enumerate(image_urls):
                    with cols[j]:
                        st.image(url, width=200)
            time.sleep(1.5)
            image_placeholder.empty()

    elif (st.session_state.button_name_clicked == 'feeds'):
        content.empty()

        cols = st.columns([2, 1])
        with cols[0]:
            st.markdown("There are different types of **OpenActive** data feeds. ")
            st.markdown(" ")
            st.markdown("Some are designed to be read together:")
            st.markdown(" - A Session Series feed includes details that apply to a number of events: location, activity, organiser, etc")
            st.markdown(" - A Scheduled Session feed includes details that apply to a specific event: date, time, number of spaces remaining, etc")
            st.markdown("Similarly:")
            st.markdown(" - A FacilityUse feed includes details that apply to a number of bookable time slots: location, type of facility, organiser, etc")
            st.markdown(" - A Slot feed includes details that apply to a specific time slot: date, time, etc")

        with cols[1]:
            # Convert the dictionary to a DataFrame for Streamlit display
            df_feed_types = pd.DataFrame(list(st.session_state.feed_type_counts.items()), columns=['Feed Type', 'Count'])
            # Sort the DataFrame by 'Count' in descending order
            df_feed_types = df_feed_types.sort_values(by='Count', ascending=False)
            # Display the table
            st.dataframe(df_feed_types, use_container_width=True, hide_index=True)

        st.markdown(" ")
        st.markdown(f"This snapshot includes data from {st.session_state.aggregate_analysis['num_feeds_preview']} 'preview' feeds - these are work in progress and not yet recognised as OpenActive compliant, but may be of interest to data users for exploratory use.")
        st.markdown("You can explore each data feed using the **[visualiser](https://visualiser.openactive.io/)** which includes some high-level data quality metrics.")

    elif (st.session_state.button_name_clicked == 'activities'):
        content.empty()
        cols = st.columns([2, 1])
        with cols[0]:
            st.markdown("The official **OpenActive** vocabularies list over 700 [activities](https://activity-list.openactive.io/en/hierarchical_concepts.html) and around 35 [facility types](https://facility-types.openactive.io/en/hierarchical_concepts.html).")
            st.markdown(" ")
            st.markdown("Using standardised names helps improve user experience and search, though publishers can and do use their own wording for activity and facility labels.")
            st.markdown(" ")
            st.write(f"There are currently **{st.session_state.aggregate_analysis['total_num_activities'] + st.session_state.aggregate_analysis['total_num_facilities']:,}** different activities and facility types in the OpenActive data.")

        with cols[1]:
            st.dataframe(
                st.session_state.aggregate_analysis['df_total_activitiesfacilities_counts'][['activity', 'percentage']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'activity': 'Activity / Facility',
                    'percentage': st.column_config.NumberColumn(
                        '%',
                        format='%0.1f',
                        help='% of OpenActive opportunities'
                    ),
                },
            )

    elif st.session_state.button_name_clicked == 'opportunities':
        content.empty()
        cols = st.columns([2, 1])
        with cols[0]:
            st.markdown("**OpenActive** describes standards to make sharing information about *'opportunities for sport and physical activity'* easier and more effective.")
            st.markdown(" ")
            st.markdown("We use the word 'opportunity' to describe the individual items or records that are contained in data feeds.")
            st.markdown(" ")
            st.markdown("Because the feeds vary in level of detail they represent (e.g. a series of sessions or an individual session), the total 'opportunity' count is quite a crude measure. But generally, an increase in total opportunities shows that more activity and facility data is being made open, and we think that is a good thing!")
            st.markdown(" ")
            st.markdown(f"Right now, OpenActive data contains **{millify(st.session_state.aggregate_analysis['total_num_future_opportunity_items'], precision=1)} opportunities** to get active over the coming weeks.")

        with cols[1]:
            fig, ax = plt.subplots(1, 1, figsize=(3, 6))
            plt.style.use('ggplot')
            st.session_state.aggregate_analysis['gdf_total_regions_counts'].plot(
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
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    #Need more historic datapoints to make this a compelling visual
    # dated_counts = {
    #     'Jan 17': 0,
    #     'Jul 17': 80000,
    #     'Jan 18': 80000,
    #     'Jul 18': 110000,
    #     'Jan 19': 160000,
    #     'Jun 19': 200000,
    # }

    # current_month = datetime.now().strftime('%b %y')
    # dated_counts[current_month] = st.session_state.aggregate_analysis['total_num_items']
    # df = pd.DataFrame.from_dict(dated_counts, orient='index', columns=['Count'])
    # df.reset_index(inplace=True)
    # df.columns = ['Date', 'Count']
    # df['Date'] = pd.to_datetime(df['Date'], format='%b %y')
    # df = df.sort_values(by='Date')

    # st.line_chart(df, x='Date', y='Count')

# --------------------------------------------------------------------------------------------------

    elif st.session_state.button_name_clicked == 'kpis':
        content.empty()
        st.markdown('**Key Performance Indicators**')
        st.markdown('**Growth of OpenActive**')
        st.markdown(f"***{st.session_state.aggregate_analysis['percentage_sad_matched']:.1f}% of Sport England recognised Sports and Disciplines appear in OpenActive data feeds***")
        with st.expander('This is a simple measure of coverage across sports in the OpenActive ecosystem.\n\nClick here for more details.'):
            st.write(f"{st.session_state.aggregate_analysis['num_sad_matched']} of the {st.session_state.aggregate_analysis['num_sad']} recognised Sports and Disciplines found in OpenActive data ({st.session_state.aggregate_analysis['percentage_sad_matched']:.1f}%)")
            st.dataframe(
                combined_SE_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "sport_and_discipline": "Sports and Disciplines",
                    "activity": "Activities and Facilities in OpenActive data",
                    "% of Opportunities": st.column_config.NumberColumn(
                        "% of Opportunities", format="%0.1f"
                    ),
                },
            )

            #Removed for now - these should be future opportunities
            #st.write(f"Num. activities: {st.session_state.aggregate_analysis['total_num_activities_with_sad']:,}")
            #st.write(f"Num. opportunities: {st.session_state.aggregate_analysis['total_num_items_with_sad']:,}")

            st.divider()
            st.write('Sports and Disciplines')
            st.markdown('These are the sports governed by the list of national governing bodies recognised by the UK Sports Councils. Source: spreadsheet downloaded from the [Sport England website](https://www.sportengland.org/guidance-and-support/national-governing-bodies?section=recognised_ngbs) on 2024-01-24.')
            st.write('Disciplines are categories within each of the recognised sports. For example: "crown", "federation", and "short mat" are all distinct disciplines of bowls.')

        gdf = st.session_state.aggregate_analysis['gdf_total_districts_counts']

        # Filter for counts 50 or greater (important to include NaNs as 'not greater than or equal to 50')
        gdf_filtered = gdf[(gdf['count'] >= 1000) | (gdf['count'].isna())]

        # Calculate the percentage
        percentage_1000_or_more = (len(gdf_filtered) / len(gdf)) * 100

        st.markdown(f"***{percentage_1000_or_more:.1f}% of UK Local Authority areas have more than 1000 opportunities across the OpenActive data feeds***")
        with st.expander('This is a simple measure of UK coverage in the OpenActive ecosystem.\n\nClick here for more details.'):

            st.write(f"{len(gdf_filtered)} of the {len(gdf)} Local Authorities in the UK have more than 1000 opportunities in OpenActive data ({percentage_1000_or_more:.1f}%)")

            cols = st.columns(2)
            with cols[0]:

                st.dataframe(
                    st.session_state.aggregate_analysis['gdf_total_districts_counts'][['LAD24NM', 'count', 'percentage']],
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
                #st.write(f"Num. locations: {st.session_state.aggregate_analysis['total_num_districts']:,}")
                #st.write(f"Num. opportunities: {st.session_state.aggregate_analysis['total_num_items_with_districts']:,}")
            with cols[1]:
                fig, ax = plt.subplots(1, 1, figsize=(8, 8))
                st.session_state.aggregate_analysis['gdf_total_districts_counts'].plot(
                    column='percentage',
                    # cmap='YlOrRd',
                    cmap='inferno_r',
                    legend=True,
                    ax=ax,
                )
                ax.set(facecolor='white')
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title('% of OA opportunities by Local Authority')
                st.pyplot(fig)
                plt.close(fig)

            st.markdown(" ")
            st.divider()
            st.write(f"Using November 2024 data, we explored the coverage of local areas in OpenActive data feeds.")
            st.write("There are over 32,000 [Lower Layer Super Output Areas (LSOAs)](https://www.ons.gov.uk/methodology/geography/ukgeographies/statisticalgeographies) in England, with populations between 1000 and 3000 people. These are ranked by the Office of National Statistics by indicators of deprivation.")
            st.write("Less than 30% of most deprived areas appear in OpenActive data, compared to almost 50% of the least deprived areas.")
            # LSOAs by deprivation deciles
            data = """Most Deprived,	945,	3285
            2,	1037,	3284
            3,	1189,	3284
            4,	1289,	3285
            5,	1360,	3284
            6,	1451,	3284
            7,	1478,	3285
            8,	1557,	3284
            9,	1504,	3284
            Least Deprived,	1560,	3285"""

            # Convert the string data to DataFrame
            from io import StringIO  # For string data
            df = pd.read_csv(StringIO(data), header=None, names=['decile', 'LSOA count', 'LSOA total count'])

            # Calculate percentage
            df['percentage'] = (df['LSOA count'] / df['LSOA total count']) * 100

            decile_labels = ['Most Deprived', '2', '3', '4', '5', '6', '7', '8', '9', 'Least Deprived']

            fig = go.Figure(go.Bar(
                y=df['percentage'],
                x=decile_labels,  # Use string labels directly
                orientation='v',
                marker_color='#e11482',
            ))

            fig.update_layout(
                title="OA coverage across LSOAs, ranked by deprivation index",
                xaxis_title="LSOAs grouped by deprivation index",
                yaxis_title="% of LSOAs in each group with OpenActive opportunities",
                height=600,
                yaxis_range=[0, 100],
                xaxis = dict(
                    type = 'category' #This tells Plotly to treat the x-axis as categorical
                )
            )
            # Display chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            st.write(' ')

        st.markdown(f"***{percentage_1000_or_more:.1f}% of UK Local Authority areas have more than 1000 opportunities across the OpenActive data feeds***")
        with st.expander('This is a simple measure of UK coverage in the OpenActive ecosystem.\n\nClick here for more details.'):
            
            st.write(f"{len(gdf_filtered)} of the {len(gdf)} Local Authorities in the UK have more than 1000 opportunities in OpenActive data ({percentage_1000_or_more:.1f}%)")
            
            # Get the geodataframe
            gdf_districts = st.session_state.aggregate_analysis['gdf_total_districts_counts'].copy()
            
            # Text input for filtering by district name (on top)
            search_term = st.text_input(
                'Search districts by name',
                placeholder='Type to filter districts (e.g., "Manchester", "London")...', 
                key='district_search'
            )
            
            # Filter the dataframe based on search term
            if search_term:
                filtered_gdf = gdf_districts[gdf_districts['LAD24NM'].str.contains(search_term, case=False, na=False)]
            else:
                filtered_gdf = gdf_districts
            
            st.write(f"Showing {len(filtered_gdf)} of {len(gdf_districts)} districts")
            
            # Create two columns for table and map side by side (1:2 ratio)
            col_table, col_map = st.columns([1, 2])
            
            with col_table:
                # Prepare dataframe for display
                display_df = filtered_gdf[['LAD24NM', 'count', 'percentage']].sort_values('LAD24NM').reset_index(drop=True)
                display_df = display_df.rename(columns={
                    'LAD24NM': 'District Name',
                    'count': 'Num. Opportunities',
                    'percentage': '% of Total',
                })
                
                # Configure AgGrid for cell click selection
                gb = GridOptionsBuilder.from_dataframe(display_df)
                gb.configure_column('District Name', cellStyle={'cursor': 'pointer'})
                gb.configure_column('Num. Opportunities', type=['numericColumn'], valueFormatter="Math.round(x).toLocaleString()", maxWidth=120)
                gb.configure_column('% of Total', type=['numericColumn'], valueFormatter="x.toFixed(2) + '%'", maxWidth=120)
                gb.configure_selection(selection_mode='single', use_checkbox=False)
                grid_options = gb.build()
                
                # Display AgGrid table with cell click
                st.caption('Click a District Name to highlight on map')
                grid_response = AgGrid(
                    display_df,
                    gridOptions=grid_options,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    height=450,
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                )
                
                # Get selected district from cell click
                selected_district = None
                selected_rows = grid_response.get('selected_rows', None)
                if selected_rows is not None and len(selected_rows) > 0:
                    selected_district = selected_rows.iloc[0]['District Name']
            
            with col_map:
                # Create leafmap with the data
                # Ensure we have valid geometry and reproject to WGS84 for leafmap
                map_gdf = filtered_gdf.copy()
                if map_gdf.crs is not None and map_gdf.crs != 'EPSG:4326':
                    map_gdf = map_gdf.to_crs('EPSG:4326')
                
                # Prepare data for popup - only keep desired columns and rename
                popup_columns = ['LAD24NM', 'count', 'percentage']
                if 'category' in map_gdf.columns:
                    popup_columns.append('category')
                
                # Create a copy with only the columns we need for the popup
                map_gdf_display = map_gdf[popup_columns + ['geometry']].copy()
                map_gdf_display = map_gdf_display.rename(columns={
                    'LAD24NM': 'Name',
                    'count': 'Opportunities',
                    'percentage': 'Percentage',
                })
                
                # UK bounding box: SW corner [49.5, -8.5], NE corner [61, 2]
                uk_bounds = [[49.5, -8.5], [61, 2]]
                
                # Create the map centered on UK with max_bounds to restrict panning
                m = leafmap.Map(
                    center=[54.5, -2], 
                    zoom=6,
                    max_bounds=True,  # Restrict panning to the bounds
                )
                
                # Set max bounds to UK area to prevent showing world map
                m.options['maxBounds'] = uk_bounds
                m.options['minZoom'] = 5
                
                # Fit to UK bounds
                m.fit_bounds(uk_bounds)
                
                # Add the choropleth layer with custom popup fields
                if len(map_gdf_display) > 0:
                    m.add_data(
                        map_gdf_display,
                        column='Percentage',
                        cmap='YlOrRd',
                        legend_title='% of Opportunities',
                        layer_name='Districts',
                        style={'fillOpacity': 0.7, 'weight': 0.5},
                    )
                
                # Highlight selected district
                if selected_district is not None:
                    selected_gdf = map_gdf[map_gdf['LAD24NM'] == selected_district].copy()
                    if len(selected_gdf) > 0:
                        selected_display = selected_gdf[popup_columns + ['geometry']].copy()
                        selected_display = selected_display.rename(columns={
                            'LAD24NM': 'Name',
                            'count': 'Opportunities',
                            'percentage': 'Percentage',
                        })
                        m.add_gdf(
                            selected_display,
                            layer_name='Selected District',
                            style={
                                'fillColor': '#00FF00',
                                'fillOpacity': 0.7,
                                'color': '#000000',
                                'weight': 1,
                            },
                        )
                        # Zoom to the selected district
                        bounds = selected_gdf.total_bounds  # [minx, miny, maxx, maxy]
                        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
                
                # Display the map using st_folium
                # Use returned_objects=[] to prevent map interactions from triggering reruns
                st_folium(
                    m, 
                    use_container_width=True,
                    height=500, 
                    returned_objects=[],
                )

            st.markdown(" ")
            st.divider()
            st.write(f"Using November 2024 data, we explored the coverage of local areas in OpenActive data feeds.")
            st.write("There are over 32,000 [Lower Layer Super Output Areas (LSOAs)](https://www.ons.gov.uk/methodology/geography/ukgeographies/statisticalgeographies) in England, with populations between 1000 and 3000 people. These are ranked by the Office of National Statistics by indicators of deprivation.")
            st.write("Less than 30% of most deprived areas appear in OpenActive data, compared to almost 50% of the least deprived areas.")
            # LSOAs by deprivation deciles
            data = """Most Deprived,	945,	3285
            2,	1037,	3284
            3,	1189,	3284
            4,	1289,	3285
            5,	1360,	3284
            6,	1451,	3284
            7,	1478,	3285
            8,	1557,	3284
            9,	1504,	3284
            Least Deprived,	1560,	3285"""

            # Convert the string data to DataFrame
            from io import StringIO  # For string data
            df = pd.read_csv(StringIO(data), header=None, names=['decile', 'LSOA count', 'LSOA total count'])

            # Calculate percentage
            df['percentage'] = (df['LSOA count'] / df['LSOA total count']) * 100

            decile_labels = ['Most Deprived', '2', '3', '4', '5', '6', '7', '8', '9', 'Least Deprived']

            fig = go.Figure(go.Bar(
                y=df['percentage'],
                x=decile_labels,  # Use string labels directly
                orientation='v',
                marker_color='#e11482',
            ))

            fig.update_layout(
                title="OA coverage across LSOAs, ranked by deprivation index",
                xaxis_title="LSOAs grouped by deprivation index",
                yaxis_title="% of LSOAs in each group with OpenActive opportunities",
                height=600,
                yaxis_range=[0, 100],
                xaxis = dict(
                    type = 'category' #This tells Plotly to treat the x-axis as categorical
                )
            )
            # Display chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            st.write(' ')

#print(st.session_state.aggregate_analysis.keys())
#print(st.session_state.aggregate_analysis['total_num_districts'])
#print(st.session_state.aggregate_analysis['gdf_total_districts_counts'])

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
