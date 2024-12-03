import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import time
from datetime import date, timedelta
from millify import millify

# --------------------------------------------------------------------------------------------------

#print(st.session_state.analysis.keys())
#For reference in presenting numbers
#dict_keys(['num_publishers_regular', 'num_publishers_preview', 'num_publishers', 
# 'num_datasets_regular', 'num_datasets_preview', 'num_datasets', 
# 'num_feeds_regular', 'num_feeds_preview', 'num_feeds', 
# 'num_feeds_with_analysed_data_regular', 'num_feeds_with_analysed_data_preview', 'num_feeds_with_analysed_data', 
# 'total_num_opportunities_regular', 'total_num_opportunities_preview', 'total_num_opportunities', 
# 'total_num_opportunities_future_regular', 'total_num_opportunities_future_preview', 'total_num_opportunities_future', 
# 'total_num_opportunities_future_week_regular', 'total_num_opportunities_future_week_preview', 'total_num_opportunities_future_week', 
# 'df_total_activities_counts', 'total_num_activities', 'total_num_opportunities_with_activities', 
# 'df_total_organisers_counts', 'total_num_organisers', 'total_num_opportunities_with_organisers', 
# 'gdf_total_regions_counts', 'total_num_regions', 'total_num_opportunities_with_regions', 
# 'gdf_total_lads_counts', 'total_num_lads', 'total_num_opportunities_with_lads', 
# 'df_total_kinds_counts', 'total_num_kinds', 'total_num_opportunities_with_kinds', 
# 'df_total_types_counts', 'total_num_types', 'total_num_opportunities_with_types', 
# 'df_total_address_counts', 'total_num_address', 'total_num_opportunities_with_address', 
# 'df_total_sad_counts_matched', 'df_total_sad_counts_unmatched', 
# 'total_num_activities_with_sad', 'total_num_activities_without_sad', 'total_num_opportunities_with_sad', 'total_num_opportunities_without_sad', 
# 'num_sad', 'num_sad_matched', 'num_sad_unmatched', 
# 'percentage_sad_matched', 'percentage_sad_unmatched', 'df_se_sport_and_discipline_unmatched', 
# 'filenames_sampleitems'])

#Combine SE data for display
# Select desired columns and rename for consistency
matched_df = st.session_state.analysis['df_total_sad_counts_matched'][['sport_and_discipline', 'activity', 'percentage_opportunities']].rename(
    columns={'percentage_opportunities': '% of Opportunities'}
)
unmatched_df = st.session_state.analysis['df_se_sport_and_discipline_unmatched'][['sport_and_discipline']].rename(
    columns={}
) # Empty dictionary since only one column to select
# Concatenate and sort
combined_SE_df = pd.concat([matched_df, unmatched_df], ignore_index=True).sort_values('sport_and_discipline')

# --------------------------------------------------------------------------------------------------

if ('buttons' not in st.session_state):
    st.session_state.buttons = {
        'providers': f"**{st.session_state.analysis['num_publishers']:,}**\n\nData Providers",
        #Note next figure based on feeds.pickle to tally with type counts
        'feeds': f"**{st.session_state.num_feeds:,}**\n\nData feeds",
        'activities': f"**{st.session_state.analysis['total_num_activities']:,}**\n\nActivities and facilities",
        'opportunities': f"**{millify(st.session_state.analysis['total_num_opportunities_future'], precision=1)}**\n\nLive opportunities",
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

cols = st.columns([1, 3])

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
        st.markdown(f"**OpenActive** is a decentralised open data initiative. Each of the **{st.session_state.analysis['num_publishers']:,}** data providers shares one or more data feeds, providing near real time availability of their activities and facilities.")
        st.markdown(" ")
        st.markdown("""The <a href="https://status.openactive.io/" target="_blank"><b>status page</b></a> lists the data providers and basic information about the status of each feed.""", unsafe_allow_html=True)
        st.markdown(" ")
        st.markdown("Some data providers are National Governing Bodies, some are big leisure providers, while others create systems to allow smaller activity providers to open their data.")
        st.markdown(" ")
        orgs = len(st.session_state.analysis['df_total_organisers_counts'])
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
        st.markdown(f"This snapshot include data from {st.session_state.analysis['num_feeds_preview']} 'preview' feeds - these are work in progress and not yet recognised as OpenActive compliant, but may be of interest to data users for exploratory use.")
        st.markdown("You can explore each data feed using the **[visualiser](https://visualiser.openactive.io/)** which includes some high-level data quality metrics.")
            
    elif (st.session_state.button_name_clicked == 'activities'):
        content.empty()
        cols = st.columns([2, 1])
        with cols[0]:
            st.markdown("The official **OpenActive** vocabularies list over 700 [activities](https://activity-list.openactive.io/en/hierarchical_concepts.html) and around 35 [facility types](https://facility-types.openactive.io/en/hierarchical_concepts.html).")
            st.markdown(" ")
            st.markdown("Using standardised names helps improve user experience and search, though publishers can and do use their own wording for activity and facility labels.")
            st.markdown(" ")
            st.write(f"There are currently **{st.session_state.analysis['total_num_activities']:,}** different activities and facility types in the OpenActive data.")

        with cols[1]:
            st.dataframe(
                st.session_state.analysis['df_total_activities_counts'][['activity','percentage']],
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
            st.markdown(f"Right now, OpenActive data contains **{millify(st.session_state.analysis['total_num_opportunities_future'], precision=1)} opportunities** to get active over the coming weeks.")

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
    # dated_counts[current_month] = st.session_state.analysis['total_num_opportunities']
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
        st.markdown(f"***{st.session_state.analysis['percentage_sad_matched']:.1f}% of Sport England recognised Sports and Disciplines appear in OpenActive data feeds***")
        with st.expander('This is a simple measure of coverage across sports in the OpenActive ecosystem.  \nClick here for more details.'):
            st.write(f"{st.session_state.analysis['num_sad_matched']} of the {st.session_state.analysis['num_sad']} recognised Sports and Disciplines found in OpenActive data ({st.session_state.analysis['percentage_sad_matched']:.1f}%)")    
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
            #st.write(f"Num. activities: {st.session_state.analysis['total_num_activities_with_sad']:,}")
            #st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_sad']:,}")

            st.divider()
            st.write('Sports and Disciplines')
            st.markdown('These are the sports governed by the list of national governing bodies recognised by the UK Sports Councils. Source: spreadsheet downloaded from the [Sport England website](https://www.sportengland.org/guidance-and-support/national-governing-bodies?section=recognised_ngbs) on 2024-01-24.')
            st.write('Disciplines are categories within each of the recognised sports. For example: "crown", "federation", and "short mat" are all distinct disciplines of bowls.')
            
        gdf = st.session_state.analysis['gdf_total_lads_counts']

        # Filter for counts 50 or greater (important to include NaNs as 'not greater than or equal to 50')
        gdf_filtered = gdf[(gdf['count'] >= 1000) | (gdf['count'].isna())]

        # Calculate the percentage
        percentage_1000_or_more = (len(gdf_filtered) / len(gdf)) * 100

        st.markdown(f"***{percentage_1000_or_more:.1f}% of UK Local Authorities have more than 1000 opportunities in OpenActive data feeds***")
        with st.expander('This is a simple measure of UK coverage in the OpenActive ecosystem.   \nClick here for more details.'):
            
            st.write(f"{len(gdf_filtered)} of the {len(gdf)} Local Authorities in the UK have more than 1000 opportunities in OpenActive data ({percentage_1000_or_more:.1f}%)")    
          
            cols = st.columns(2)
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
                #st.write(f"Num. locations: {st.session_state.analysis['total_num_lads']:,}")
                #st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_lads']:,}")
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
                ax.set_title('% of OA opportunities by Local Authority')
                st.pyplot(fig)
                plt.close(fig)

            st.markdown(" ")
            st.divider()
            st.write(f"Using November 24 data, we explored the coverage of local areas in OpenActive data feeds.")
            st.write("There are over 32,000 [Lower Layer Super Output Areas (LSOAs)](https://www.ons.gov.uk/methodology/geography/ukgeographies/statisticalgeographies) in England, with populations between 1000 and 3000 people. There are ranked by the Office of National Statistics by indicators of deprivation.")
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
                title="Percentage of OA coverage across LSOA areas, ranked by deprivation index",
                xaxis_title="LSOAs grouped by deprivation indices",
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
                            
#print(st.session_state.analysis.keys())
#print(st.session_state.analysis['total_num_lads'])
#print(st.session_state.analysis['gdf_total_lads_counts'])

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


