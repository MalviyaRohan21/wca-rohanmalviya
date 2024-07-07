import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("📊 WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("📂 Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    df['year'] = df['year'].astype(str)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        st.title('Top Statistics')

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly Timeline
        st.title("📅 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.title("📅 Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.title('🗺️ Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("🗓️ Weekly Activity Map")
        hourly_map_data = helper.hourly_activity_map(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(hourly_map_data, ax=ax)
        st.pyplot(fig)

        # finding the busiest users in the group(Group Level)
        if selected_user:
            st.title('💬 Most Active Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

            # WordCloud
            st.title('☁️ WordCloud')
            df_wc = helper.create_wordcloud(selected_user, df)
            if df_wc:
                fig, ax = plt.subplots()
                ax.imshow(df_wc)
                st.pyplot(fig)
            else:
                st.write("No word cloud available")

            # Most_Common_Words
            st.title('🔠 Most Common Words')
            most_common_df = helper.most_common_words(selected_user, df)
            if not most_common_df.empty:
                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1])
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.write("No common words available")

            # Emoji Analysis
            st.title('😊 Emoji Analysis')
            emoji_df = helper.emoji_helper(selected_user, df)
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df['Count'].head(), labels=emoji_df['Emoji'].head(),
                           autopct="%1.1f%%", textprops={'fontsize': 12})
                    st.pyplot(fig)
            else:
                st.write("No emojis used")
