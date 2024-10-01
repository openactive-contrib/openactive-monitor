import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from millify import millify

# --------------------------------------------------------------------------------------------------

tabs = st.tabs(['Ecosystem Overview', 'KPIs'])

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
        content = st.container()
        with content:
            # Display content based on button click
            if button1:
                content.empty()
                st.markdown("**OpenActive** is a decentralised open data initiative. Each data provider shares one or more data feeds, providing near real time availability of their activities and facilities.")
            elif button2:
                content.empty()
                st.markdown(" ")
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