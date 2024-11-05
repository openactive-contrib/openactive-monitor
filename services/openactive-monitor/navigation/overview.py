import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from millify import millify
import plotly.graph_objects as go
import numpy as np
import matplotlib.cm as cm

class BubbleChart:
    def __init__(self, area, bubble_spacing=0):
        """
        Setup for bubble collapse.

        Parameters
        ----------
        area : array-like
            Area of the bubbles.
        bubble_spacing : float, default: 0
            Minimal spacing between bubbles after collapsing.

        Notes
        -----
        If "area" is sorted, the results might look weird.
        """
        area = np.asarray(area)
        r = np.sqrt(area / np.pi)

        self.bubble_spacing = bubble_spacing
        self.bubbles = np.ones((len(area), 4))
        self.bubbles[:, 2] = r
        self.bubbles[:, 3] = area
        self.maxstep = 2 * self.bubbles[:, 2].max() + self.bubble_spacing
        self.step_dist = self.maxstep / 2

        # calculate initial grid layout for bubbles
        length = np.ceil(np.sqrt(len(self.bubbles)))
        grid = np.arange(length) * self.maxstep
        gx, gy = np.meshgrid(grid, grid)
        self.bubbles[:, 0] = gx.flatten()[:len(self.bubbles)]
        self.bubbles[:, 1] = gy.flatten()[:len(self.bubbles)]

        self.com = self.center_of_mass()

    def center_of_mass(self):
        return np.average(
            self.bubbles[:, :2], axis=0, weights=self.bubbles[:, 3]
        )

    def center_distance(self, bubble, bubbles):
        return np.hypot(bubble[0] - bubbles[:, 0],
                        bubble[1] - bubbles[:, 1])

    def outline_distance(self, bubble, bubbles):
        center_distance = self.center_distance(bubble, bubbles)
        return center_distance - bubble[2] - \
            bubbles[:, 2] - self.bubble_spacing

    def check_collisions(self, bubble, bubbles):
        distance = self.outline_distance(bubble, bubbles)
        return len(distance[distance < 0])

    def collides_with(self, bubble, bubbles):
        distance = self.outline_distance(bubble, bubbles)
        return np.argmin(distance, keepdims=True)

    def collapse(self, n_iterations=50):
        """
        Move bubbles to the center of mass.

        Parameters
        ----------
        n_iterations : int, default: 50
            Number of moves to perform.
        """
        for _i in range(n_iterations):
            moves = 0
            for i in range(len(self.bubbles)):
                rest_bub = np.delete(self.bubbles, i, 0)
                # try to move directly towards the center of mass
                # direction vector from bubble to the center of mass
                dir_vec = self.com - self.bubbles[i, :2]

                # shorten direction vector to have length of 1
                dir_vec = dir_vec / np.sqrt(dir_vec.dot(dir_vec))

                # calculate new bubble position
                new_point = self.bubbles[i, :2] + dir_vec * self.step_dist
                new_bubble = np.append(new_point, self.bubbles[i, 2:4])

                # check whether new bubble collides with other bubbles
                if not self.check_collisions(new_bubble, rest_bub):
                    self.bubbles[i, :] = new_bubble
                    self.com = self.center_of_mass()
                    moves += 1
                else:
                    # try to move around a bubble that you collide with
                    # find colliding bubble
                    for colliding in self.collides_with(new_bubble, rest_bub):
                        # calculate direction vector
                        dir_vec = rest_bub[colliding, :2] - self.bubbles[i, :2]
                        dir_vec = dir_vec / np.sqrt(dir_vec.dot(dir_vec))
                        # calculate orthogonal vector
                        orth = np.array([dir_vec[1], -dir_vec[0]])
                        # test which direction to go
                        new_point1 = (self.bubbles[i, :2] + orth *
                                      self.step_dist)
                        new_point2 = (self.bubbles[i, :2] - orth *
                                      self.step_dist)
                        dist1 = self.center_distance(
                            self.com, np.array([new_point1]))
                        dist2 = self.center_distance(
                            self.com, np.array([new_point2]))
                        new_point = new_point1 if dist1 < dist2 else new_point2
                        new_bubble = np.append(new_point, self.bubbles[i, 2:4])
                        if not self.check_collisions(new_bubble, rest_bub):
                            self.bubbles[i, :] = new_bubble
                            self.com = self.center_of_mass()

            if moves / len(self.bubbles) < 0.1:
                self.step_dist = self.step_dist / 2

    def plot(self, ax, labels, colors):
        """
        Draw the bubble plot.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
        labels : list
            Labels of the bubbles.
        colors : list
            Colors of the bubbles.
        """
        for i in range(len(self.bubbles)):
            circ = plt.Circle(
                self.bubbles[i, :2], self.bubbles[i, 2]*0.95, color=colors[i]
            )
            ax.add_patch(circ)

            # Split label if longer than 30 characters, word-wise
            split_label = ""
            current_line = ""
            words = labels[i].split()
            for word in words:
                if len(current_line + word) <= 12:
                    current_line += word + " "
                else:
                    split_label += current_line.strip() + "\n"
                    current_line = word + " "
            split_label += current_line.strip()  # Add the last line


            ax.text(
                *self.bubbles[i, :2], 
                f"{split_label}\n({int(self.bubbles[i, 3])})",  # Add count to label
                horizontalalignment='center',
                verticalalignment='center',
                color='white',
                fontsize=8,
                wrap=True
            )

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
                cols = st.columns([1, 4, 1])
                with cols[1]:
                    # Create a colormap instance
                    cmap = cm.get_cmap('viridis')
                    # Map the colormap to your data (classification categories)
                    norm = plt.Normalize(vmin=0, vmax=len(st.session_state.publishers['Classification']))
                    colors = [cmap(norm(i)) for i in range(len(st.session_state.publishers['Classification']))]
                    bubble_chart = BubbleChart(area=st.session_state.publishers['Count'], bubble_spacing=0.01)
                    bubble_chart.collapse()
                    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"))  # Adjust figsize as needed
                    bubble_chart.plot(ax, st.session_state.publishers['Classification'], colors)
                    ax.axis("off")
                    ax.relim()
                    ax.autoscale_view()
                    # Display the chart in Streamlit
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)  # Close the figure to avoid potential issues
                
                st.markdown("The **status page** lists the data providers and basic information about the status of each feed.")
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