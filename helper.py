from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
extract = URLExtract()


def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Fetch number of messages
    num_messages = df.shape[0]

    # Fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # Fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    df.columns = ['user', 'percent']
    return x, df


def create_wordcloud(selected_user, df):
    with open('stop_words.txt', 'r') as f:
        stop_words = f.read().splitlines()

    temp = df[df['user'] != 'group-notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    if selected_user != 'Overall':
        temp = temp[temp['user'] == selected_user]

    if temp.empty:
        return None

    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])

    temp['message'] = temp['message'].apply(remove_stop_words)
    combined_message = temp['message'].str.cat(sep=" ")

    if combined_message.strip() == "":
        return None

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    try:
        df_wc = wc.generate(combined_message)
    except ValueError:
        return None

    return df_wc


def most_common_words(selected_user, df):
    with open('stop_words.txt', 'r') as f:
        stop_words = f.read().splitlines()

    # Apply filtering for both overall and specific users
    temp = df[df['user'] != 'group-notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    # Filter messages by the selected user if not 'Overall'
    if selected_user != 'Overall':
        temp = temp[temp['user'] == selected_user]

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    if not words:
        return pd.DataFrame(columns=['Word', 'Count'])

    most_common_df = pd.DataFrame(Counter(words).most_common(10))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    if not emojis:
        return pd.DataFrame(columns=['Emoji', 'Count'])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['Emoji', 'Count'])

    return emoji_df


def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline_data = df.groupby('only_date').count()['message'].reset_index()

    return timeline_data


def week_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def hourly_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    hourly_map_data = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return hourly_map_data
