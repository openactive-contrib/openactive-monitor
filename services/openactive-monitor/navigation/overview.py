import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from millify import millify

# --------------------------------------------------------------------------------------------------

cols = st.columns([1, 1, 2])
with cols[0]:
    st.metric(
        'Publishers',
        f"{st.session_state.analysis['num_publishers']:,}",
        help='OpenActive is a decentralised open data initiative. Each data publisher shares one or more data sets, each with one or more data feeds, providing near real time availability of their activities and facilities.',
    )
    st.metric(
        'Data sets',
        f"{st.session_state.analysis['num_datasets']:,}",
    )
    st.metric(
        'Data feeds',
        f"{st.session_state.analysis['num_feeds']:,}",
    )
    st.metric(
        'Activities and facilities',
        f"{st.session_state.analysis['total_num_activities']:,}",
        help='While the official OpenActive activity list contains over 700 standardised activity names, publishers can and do use their own wording for activity and facility names.',
    )
    st.metric(
        'Live opportunities',
        millify(st.session_state.analysis['total_num_opportunities'], precision=1),
        help='OpenActive describes standards to make sharing information about "opportunities for sport and physical activity" easier and more effective. We use the word "opportunity" to describe the individual items or records that are contained in data feeds. Because the feeds vary in level of detail they represent, the total "opportunity" count is quite a crude measure. But generally, an increase in total opportunities shows that more activity and facility data is being made open, and we think that is a good thing!',
    )
with cols[1]:
    fig, ax = plt.subplots(1, 1, figsize=(5, 10))
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
    colorbar = plt.colorbar(scalarmappable, orientation='horizontal', pad=-0.04)
    colorbar.set_label('%')
    st.pyplot(fig)
    plt.close(fig)

st.write(f"These figures include data from {st.session_state.analysis['num_feeds_preview']} preview feeds with {millify(st.session_state.analysis['total_num_opportunities_preview'], precision=1)} preview opportunities.")
st.write(f'This snapshot of the OpenActive ecosystem was created on {datetime.now().date()}.')

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