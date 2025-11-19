import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import random
import seaborn as sns
import streamlit as st
from datetime import datetime

# --------------------------------------------------------------------------------------------------

def get_value(data, key_to_find, child_key_to_find=None, continue_to_next_layer=True):
    # This function accepts key_to_find as either a single string or a list of string variants e.g. ['type', '@type'],
    # so if we receive a string then convert to a list for standard internal handling:
    if (isinstance(key_to_find, str)):
        key_to_find = [key_to_find]

    if (isinstance(data, dict)):
        for key, val in data.items():
            if (key in key_to_find):
                if (child_key_to_find is None):
                    return val
                else:
                    # If we are seeking a parent-child key pair and have found the parent key, then child_key_to_find becomes
                    # key_to_find for the next layer search. We also only want to search the immediate next layer and not
                    # beyond, hence the keyword setting here:
                    return get_value(val, child_key_to_find, continue_to_next_layer=False)
            elif (continue_to_next_layer):
                value = get_value(val, key_to_find, child_key_to_find, continue_to_next_layer)
                if (value is not None):
                    return value

    if (isinstance(data, list)):
        values = [get_value(val, key_to_find, child_key_to_find, continue_to_next_layer) for val in data]
        if (any(values)):
            return values

    return None

# --------------------------------------------------------------------------------------------------

def parse_date(date_string):
    if (isinstance(date_string, list)):
        date_string = date_string[0]

    date_formats = [
        '%Y-%m-%dT%H:%M:%SZ', # ISO 8601 format
        '%Y-%m-%d %H:%M:%S', # Common date/time format
        '%Y-%m-%d', # Date only format
        '%Y/%m/%d', # Another common date format
        '%Y-%m-%dT%H:%M:%S.%fZ', # ISO 8601 with milliseconds
        '%Y-%m-%dT%H:%M:%S.%f', # ISO 8601 with milliseconds (no Z)
        '%Y-%m-%dT%H:%M:%S%z', # ISO 8601 with timezone offset
        '%Y-%m-%dT%H:%M:%S%Z', # ISO 8601 with timezone name
    ]

    for date_format in date_formats:
        try:
            parsed_datetime = datetime.strptime(date_string, date_format)
            formatted_date = parsed_datetime.strftime('%a %d %b %I%p').replace(' 0', ' ')
            return formatted_date
        except:
            pass

    return date_string

# --------------------------------------------------------------------------------------------------

def set_sampleitems():
    st.session_state.sampleitems = []

    # st.session_state.filenames_sampleitems is a set of nested dictionaries:
    # {
    #     'filename1': {
    #         'filename1_item1_idx': {filename1_item1},
    #         'filename1_item2_idx': {filename1_item2},
    #         etc.
    #     },
    #     'filename2': {
    #         'filename2_item1_idx': {filename2_item1},
    #         'filename2_item2_idx': {filename2_item2},
    #         etc.
    #     },
    #     etc.
    # }

    # Each element in this list is itself a list of sample items from a specific feed:
    random_feed_sampleitems = random.sample(
        [list(val.values()) for val in st.session_state.filenames_sampleitems.values()],
        min(st.session_state.num_feeds_with_sampleitems,
            st.session_state.max_num_random_feeds_with_sampleitems
        )
    )

    for feed_sampleitems in random_feed_sampleitems:
        item = random.choice(feed_sampleitems)
        item_filtered = {
            'id': get_value(item, 'id'),
            'kind': get_value(item, 'kind'),
            'type': get_value(item, 'data', ['type', '@type']),
            'name': get_value(item, 'data', 'name'),
            'url': get_value(item, 'data', 'url'),
            'description': get_value(item, 'data', 'description'),
            'activities': get_value(item, 'activity', 'prefLabel'),
            'facilities': get_value(item, 'facilityType', 'prefLabel'),
            'startdate': parse_date(get_value(item, 'startDate')),
            'duration': get_value(item, 'duration'),
            'min_age': get_value(item, 'ageRange', 'minValue'),
            'max_age': get_value(item, 'ageRange', 'maxValue'),
            'offer_name': get_value(item, 'offers', 'name'),
            'offer_url': get_value(item, 'offers', 'url'),
            'offer_price': get_value(item, 'offers', 'price'),
            'offer_currency': get_value(item, 'offers', 'priceCurrency'),
            'organiser_name': get_value(item, 'organizer', 'name'),
            'organiser_url': get_value(item, 'organizer', 'url'),
            'organiser_email': get_value(item, 'organizer', 'email'),
            'organiser_telephone': get_value(item, 'organizer', 'telephone'),
            'location_name': get_value(item, 'location', 'name'),
            'location_url': get_value(item, 'location', 'url'),
            'location_email': get_value(item, 'location', 'email'),
            'location_telephone': get_value(item, 'location', 'telephone'),
            'address': get_value(item, 'address', 'streetAddress'),
            'postcode': get_value(item, 'address', 'postalCode'),
            'latitude': get_value(item, 'geo', 'latitude'),
            'longitude': get_value(item, 'geo', 'longitude'),
            'image': get_value(item, 'logo', 'url'),
        }
        st.session_state.sampleitems.append((item, item_filtered))

# --------------------------------------------------------------------------------------------------

tabs = st.tabs(['This week', 'Activities', 'Organisers', 'Locations', 'Labels', 'KPIs'])
idx_tab = 0

# --------------------------------------------------------------------------------------------------

with tabs[idx_tab]:
    idx_tab += 1

    st.header('OpenActive opportunities over the next 7 days')

    if ('sampleitems' not in st.session_state):
        set_sampleitems()

    cols = st.columns(3)
    with cols[1]:
        st.metric(
            'Live opportunities over the next 7 days',
            f"{st.session_state.analysis['total_num_opportunities_future_week']:,}",
        )

    st.divider()

    st.subheader('Example OpenActive opportunities')
    st.button(
        'Show some more examples',
        type='primary',
        on_click=set_sampleitems,
    )

    for idx_col, col in enumerate(st.columns(st.session_state.max_num_random_feeds_with_sampleitems)):
        if (idx_col == len(st.session_state.sampleitems)):
            break
        with col:
            item_filtered = st.session_state.sampleitems[idx_col][1]

            item_activity = item_filtered['activities'][0] if isinstance(item_filtered['activities'], list) else item_filtered['activities']
            item_facility = item_filtered['facilities'][0] if isinstance(item_filtered['facilities'], list) else item_filtered['facilities']
            item_offer_name = item_filtered['offer_name'][0] if isinstance(item_filtered['offer_name'], list) else item_filtered['offer_name']
            item_startdate = item_filtered['startdate'][0] if isinstance(item_filtered['startdate'], list) else item_filtered['startdate']
            item_type = item_filtered['type'][0] if isinstance(item_filtered['type'], list) else item_filtered['type']
            item_image = item_filtered['image'][0] if isinstance(item_filtered['image'], list) else item_filtered['image']
            try:
                item_latitude = float(item_filtered['latitude'][0] if isinstance(item_filtered['latitude'], list) else item_filtered['latitude'])
            except:
                item_latitude = None
            try:
                item_longitude = float(item_filtered['longitude'][0] if isinstance(item_filtered['longitude'], list) else item_filtered['longitude'])
            except:
                item_longitude = None

            st.html(f'''
                <div class="opportunity-card-top">
                    <div>
                        {f'<p style="text-decoration: underline;">{item_activity or item_facility}</p>' if ((item_activity or item_facility) is not None) else ''}
                        {f'<p>{item_offer_name}</p>' if (item_offer_name is not None) else ''}
                        {f'<p>{item_startdate}</p>' if (item_startdate is not None) else ''}
                        {f'<p>({item_type})</p>' if (item_type is not None) else ''}
                    </div>
                    <div>
                        <img src={item_image} alt=""></img>
                    </div>
                </div>
            ''')

            if (    (item_latitude is not None)
                and (item_longitude is not None)
            ):
                fig = px.scatter_mapbox(
                    pd.DataFrame({'latitude': [item_latitude], 'longitude': [item_longitude]}),
                    color_discrete_sequence=['#e11482'],
                    lat='latitude',
                    lon='longitude',
                    zoom=6,
                )
                fig.update_layout(
                    height=150,
                    mapbox_style='open-street-map',
                    margin={'t':0, 'r':0, 'b':0, 'l':0},
                )
                fig.update_traces(marker=dict(size=10))
                st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------------------------------------

with tabs[idx_tab]:
    idx_tab += 1

    st.header('OpenActive opportunities by activity')

    cols = st.columns([1, 2])
    with cols[0]:
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
    with cols[1]:
        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        sns.barplot(
            st.session_state.analysis['df_total_activities_counts'][:st.session_state.num_activities_top],
            x='count',
            y='activity',
            ax=ax,
        )
        ax.set_xlabel('Num. opportunities')
        ax.set_ylabel('OA activity')
        ax.set_title(f'Top {st.session_state.num_activities_top} live OA activities')
        ax.bar_label(ax.containers[0], fontsize=8)
        st.pyplot(fig)
        plt.close(fig)

# --------------------------------------------------------------------------------------------------

with tabs[idx_tab]:
    idx_tab += 1

    st.header('OpenActive opportunities by organiser')

    cols = st.columns([1, 2])
    with cols[0]:
        st.dataframe(
            st.session_state.analysis['df_total_organisers_counts'],
            use_container_width=True,
            hide_index=True,
            column_config={
                'organiser': 'OA organiser',
                'count': 'Num. opportunities',
                'percentage': st.column_config.NumberColumn(
                    '% opportunities',
                    format='%0.1f',
                ),
            },
        )
        st.write(f"Num. organisers: {st.session_state.analysis['total_num_organisers']:,}")
        st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_organisers']:,}")
    with cols[1]:
        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        sns.barplot(
            st.session_state.analysis['df_total_organisers_counts'][:st.session_state.num_activities_top],
            x='count',
            y='organiser',
            ax=ax,
        )
        ax.set_xlabel('Num. opportunities')
        ax.set_ylabel('OA organiser')
        ax.set_title(f'Top {st.session_state.num_activities_top} live OA organisers')
        ax.bar_label(ax.containers[0], fontsize=8)
        st.pyplot(fig)
        plt.close(fig)

# --------------------------------------------------------------------------------------------------

with tabs[idx_tab]:
    idx_tab += 1

    st.header('OpenActive opportunities by location')

    cols = st.columns(3)
    with cols[0]:
        st.dataframe(
            st.session_state.analysis['gdf_total_regions_counts'][['eer18nm', 'count', 'percentage']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'eer18nm': 'Location',
                'count': 'Num. opportunities',
                'percentage': st.column_config.NumberColumn(
                    '% opportunities',
                    format='%0.1f',
                ),
            },
        )
        st.write(f"Num. locations: {st.session_state.analysis['total_num_regions']:,}")
        st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_regions']:,}")
    with cols[1]:
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        st.session_state.analysis['gdf_total_regions_counts'].plot(
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

# --------------------------------------------------------------------------------------------------

with tabs[idx_tab]:
    idx_tab += 1

    st.header('OpenActive opportunities by label')

    cols = st.columns(2)
    with cols[0]:
        st.dataframe(
            st.session_state.analysis['df_total_kinds_counts'],
            use_container_width=True,
            hide_index=True,
            column_config={
                'kind': 'OA kind',
                'count': 'Num. opportunities',
                'percentage': st.column_config.NumberColumn(
                    '% opportunities',
                    format='%0.1f',
                ),
            },
        )
        st.write(f"Num. kinds: {st.session_state.analysis['total_num_kinds']:,}")
        st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_kinds']:,}")
    with cols[1]:
        st.dataframe(
            st.session_state.analysis['df_total_types_counts'],
            use_container_width=True,
            hide_index=True,
            column_config={
                'type': 'OA type',
                'count': 'Num. opportunities',
                'percentage': st.column_config.NumberColumn(
                    '% opportunities',
                    format='%0.1f',
                ),
            },
        )
        st.write(f"Num. types: {st.session_state.analysis['total_num_types']:,}")
        st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_with_types']:,}")

# --------------------------------------------------------------------------------------------------

with tabs[idx_tab]:
    idx_tab += 1

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

        # st.write('Unmatched OA activities')
        # st.dataframe(
        #     st.session_state.analysis['df_total_sad_counts_unmatched'],
        #     hide_index=True,
        #     column_config={
        #         'sport_and_discipline': 'SE sport and discipline',
        #         'activity': 'OA activity',
        #         'count_opportunities': 'Num. opportunities',
        #         'percentage_opportunities': st.column_config.NumberColumn(
        #             '% opportunities',
        #             format='%0.1f',
        #         ),
        #     },
        # )
        # st.write(f"Num. activities: {st.session_state.analysis['total_num_activities_without_sad']:,}")
        # st.write(f"Num. opportunities: {st.session_state.analysis['total_num_opportunities_without_sad']:,}")