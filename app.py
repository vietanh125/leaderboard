import gradio as gr
import numpy as np
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
rename = {'thumbs_up_ratio': 'thumbs_up', 'is_custom_reward': 'custom_reward', 'user_writing_speed': 'writing_speed', 'safety_score':'safety', 'total_feedback_count': 'feedbacks'}
def get_db_prize(records):
    prize = ['🥇 $10000', '🥈 $5000', '🥉 $2000', '🎖️ $1000', '🎖️ $750'] + ['🏃‍♀️ $250']*15
    df = pd.read_csv('db.csv')
    df['overall_rank'] = df['overall_rank'].rank().astype(int)
    df = df.drop_duplicates('developer_uid', keep='first').reset_index(drop=True)
    df = df.drop(columns=['repetition', 'model_repo'])
    df = df.rename(columns=rename)
    if len(prize) > len(df):
        prize = prize[:len(df)]
    else:
        prize = prize + [""] * (len(df) - len(prize))
    df['Prize'] = prize
    update = 'Last updated ' + display_time(time.time() - df.loc[0]['last_updated']) + ' ago.'
    df = df.drop(['last_updated'], axis=1)
    df = df.round(5)
    return update, df

def get_db(records):
    df = pd.read_csv('db.csv')
    df['overall_rank'] = df['overall_rank'].rank().astype(int)
    df = df.drop(columns=['repetition', 'model_repo'])
    df = df.rename(columns=rename)
    update = 'Last updated ' + display_time(time.time() - df.loc[0]['last_updated']) + ' ago.'
    df = df.drop(['last_updated'], axis=1)
    df = df.round(5)
    return update, df

page1 = gr.Interface(
        fn=get_db_prize,
        inputs=None,
        wrap=True,
        outputs=[gr.Text(label='History'), gr.DataFrame(label='💎 Leaderboard')],
        interactive=False,
        allow_flagging='never',
    )
page2 = gr.Interface(
        fn=get_db,
        inputs=None,
        wrap=True,
        allow_flagging='never',
        outputs=[gr.Text(label='History'), gr.DataFrame(label='💎 Leaderboard')],
        interactive=False
    )
demo = gr.TabbedInterface([page1, page2], ["💰 Prize Leaderboard", "ℹ️ Detailed Leaderboard"])

if __name__ == "__main__":
    demo.launch()
