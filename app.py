import gradio as gr
import pandas as pd
import time 


intervals = (
    ('hour', 3600),    # 60 * 60
    ('min', 60),
    ('sec', 1),
)

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(int(value), name))
    return ' '.join(result[:granularity])

def get_db_prize():
    prize = ['🥇 $10000', '🥈 $5000', '🥉 $2000', '🎖️ $1000', '🎖️ $750'] + ['🏃‍ $250'] * 15
    df = pd.read_csv('db.csv')
    df = df.drop_duplicates('developer_uid', keep='first').reset_index(drop=True)
    # rename to make the table thinner
    df = df.rename(columns={'thumbs_up_ratio': 'thumbs_up', 'user_writing_speed': 'writing_speed', 'total_feedback_count': 'feedback_count'})
    if len(prize) > len(df):
        prize = prize[:len(df)]
    else:
        prize = prize + [""] * (len(df) - len(prize))
    df['Prize'] = prize
    update = 'Last updated ' + display_time(time.time() - df.loc[0]['last_updated']) + ' ago.'
    df = df.drop(['last_updated'], axis=1)
    df = df.round(5)
    return update, df

def get_db():
    df = pd.read_csv('db.csv')
    df = df.rename(columns={'thumbs_up_ratio': 'thumbs_up', 'user_writing_speed': 'writing_speed', 'total_feedback_count': 'feedback_count'})
    update = 'Last updated ' + display_time(time.time() - df.loc[0]['last_updated']) + ' ago.'
    df = df.drop(['last_updated'], axis=1)
    df = df.round(5)
    return update, df

prize_lb = gr.Interface(
        fn=get_db_prize,
        inputs=None,
        outputs=[gr.Text(label='History'), gr.DataFrame(label='💎 Leaderboard')],
        allow_flagging='never',
    )
detailed_lb = gr.Interface(
        fn=get_db,
        inputs=None,
        allow_flagging='never',
        outputs=[gr.Text(label='History'), gr.DataFrame(label='💎 Leaderboard')],
    )
demo = gr.TabbedInterface([prize_lb, detailed_lb], ["💰 Prize Leaderboard", "ℹ️ Detailed Leaderboard"])

if __name__ == "__main__":
    demo.launch()
