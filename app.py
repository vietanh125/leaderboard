import datetime
import time
import warnings

import gradio as gr
import pandas as pd
from pytz import timezone

warnings.filterwarnings("ignore")

intervals = (
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)
rename = {'thumbs_up_ratio': 'thumbs_up', 'is_custom_reward': 'custom_reward', 'user_writing_speed': 'writing_speed',
          'safety_score': 'safety', 'total_feedback_count': 'feedbacks', 'overall_rank': 'rank'}
start = datetime.datetime(2024, 1, 20, 0, 0, tzinfo=timezone('US/Pacific')).timestamp()
end = datetime.datetime(2024, 1, 30, 12, 0, tzinfo=timezone('US/Pacific')).timestamp()


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
    df = pd.read_csv('db.csv')
    df['overall_rank'] = df['overall_rank'].rank().astype(int)
    df = df.drop_duplicates('developer_uid', keep='first').reset_index(drop=True)
    df = df.rename(columns=rename)
    update = 'Last updated ' + display_time(time.time() - df.loc[0]['last_updated']) + ' ago.'
    df = df.drop(['last_updated'], axis=1)
    df = df.round(5)
    return update, df


def get_db():
    df = pd.read_csv('db.csv')
    df['overall_rank'] = df['overall_rank'].rank().astype(int)
    df = df.rename(columns=rename)
    update = 'Last updated ' + display_time(time.time() - df.loc[0]['last_updated']) + ' ago.'
    df = df.drop(['last_updated'], axis=1)
    df = df.round(5)
    return update, df


def get_db_private():
    update, _ = get_db()
    df = pd.read_csv('db_private.csv')

    prize = ['🥇 $2000', '🥈 $2000', '🥉 $1500', '🎖️ $1000', '🎖️ $1000'] + ['🏃‍♀️ $500'] * 5
    if len(prize) > len(df):
        prize = prize[:len(df)]
    else:
        prize = prize + [""] * (len(df) - len(prize))
    df['Prize'] = prize

    df = df.round(5)
    return update, df


def get_time():
    dur = end - start
    now = datetime.datetime.now(timezone('US/Pacific')).timestamp() - start
    remaining = end - time.time()
    # return now/dur, remaining
    # progress(now/dur)
    if now < 0:
        res = 'Season is not yet started.'
    elif now > dur:
        res = 'Season has ended.'
    else:
        res = display_time(remaining, 4)
    return res


theme = gr.themes.Soft(
    primary_hue="rose",
    secondary_hue="rose",
).set(
    button_secondary_background_fill='*primary_500',
    button_secondary_background_fill_dark='*primary_700',
    button_secondary_background_fill_hover='*primary_400',
    button_secondary_background_fill_hover_dark='*primary_500',
)
back_to_top_btn_html = '''
<button type="button" id="toTopBtn" onclick="'parentIFrame' in window ? window.parentIFrame.scrollTo({top: 0, behavior:'smooth'}) : window.scrollTo({ top: 0 })">
<a style="color:red; text-decoration:none;">Back to Top!</a>
</button>'''

style = """
#toTopBtn {
	position: fixed;
        bottom: 10px;
        float: right;
        right: 18.5%;
        left: 77.25%;
	height: 30px;
        max-width: 100px;
        width: 100%;
        font-size: 12px;
        border-color: rgba(217,24,120, .5);
        background-color: rgba(35,153,249,.5);
        padding: .5px;
        border-radius: 4px;
   }
"""

with gr.Blocks(theme=theme, css=style) as demo:
    with gr.Tab("🔥 Public Leaderboard"):
        text = gr.Text(label='History')
        btn = gr.Button("Refresh")
        df = gr.DataFrame(label='💎 Leaderboard')
        btn.click(fn=get_db_prize, inputs=None, outputs=[text, df])

    with gr.Tab("ℹ️ Detailed Leaderboard"):
        text2 = gr.Text(label='History')
        btn2 = gr.Button("Refresh")
        df2 = gr.DataFrame(label='💎 Leaderboard')
        btn2.click(fn=get_db, inputs=None, outputs=[text2, df2])
        gr.HTML(back_to_top_btn_html)

    with gr.Tab('⌛ Season Countdown'):
        cd = gr.Text(label='Season Time Remaining')
        prog = gr.Progress()

    demo.load(get_time, None, cd, every=1)
    demo.load(get_db_prize, None, [text, df])
    # demo.load(get_db, None, [text2, df2]) # lagging on startup

    # with gr.Tab("💰 Private Leaderboard"):
    #     text2 = gr.Text(label='History')
    #     btn2 = gr.Button("Refresh")
    #     df2 = gr.DataFrame(label='💎 Leaderboard')
    #     btn2.click(fn=get_db_private, inputs=None, outputs=[text2, df2])

if __name__ == "__main__":
    demo.queue().launch()
