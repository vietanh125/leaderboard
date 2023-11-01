import requests
import time
import datetime
from tqdm import tqdm
import pandas as pd
from chai_guanaco.feedback import _get_latest_feedback
from chai_guanaco.login_cli import auto_authenticate
from chai_guanaco.metrics import FeedbackMetrics, _add_overall_rank



LEADERBOARD_ENDPOINT = "/leaderboard"
PUBLIC_LEADERBOARD_MINIMUM_FEEDBACK_COUNT = 150
LEADERBOARD_DISPLAY_COLS = [
    'developer_uid',
    'submission_id',
    'status',
    'thumbs_up_ratio',
    'user_writing_speed',
    'repetition',
    'total_feedback_count',
    'overall_rank',
]

def get_all_historical_submissions(developer_key):
    headers = {"developer_key": developer_key}
    url = 'https://guanaco-submitter.chai-research.com/leaderboard'
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200, resp.json()
    return resp.json()

def cache(func, regenerate=False):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper

@auto_authenticate
def get_feedback(submission_id: str, developer_key=None):
    # submissions = get_all_historical_submissions(developer_key)
    # is_deployed = _submission_is_deployed(submission_id, submissions)
    # load_feedback = _get_latest_feedback if is_deployed else _get_cached_feedback
    load_feedback = _get_latest_feedback
    feedback = load_feedback(submission_id, developer_key)
    return feedback

@auto_authenticate
def display_leaderboard(
        developer_key=None,
        regenerate=False,
        detailed=False,
        ):
    df = cache(get_leaderboard, regenerate)(developer_key)
    # _print_formatted_leaderboard(df, detailed)
    return df


@auto_authenticate
def get_leaderboard(developer_key=None):
    submission_data = get_all_historical_submissions(developer_key)
    leaderboard = []
    for submission_id, meta_data in tqdm(submission_data.items(), 'Getting Metrics'):
        metrics = get_submission_metrics(submission_id, developer_key)
        meta_data.update(metrics)
        leaderboard.append({'submission_id': submission_id, **meta_data})
    return pd.DataFrame(leaderboard)


@auto_authenticate
def get_submission_metrics(submission_id, developer_key):
    feedback = get_feedback(submission_id, developer_key)
    feedback_metrics = FeedbackMetrics(feedback.raw_data)
    metrics = {}
    if len(feedback_metrics.convo_metrics) > 0:
        metrics = {
            'mcl': feedback_metrics.mcl,
            'thumbs_up_ratio': feedback_metrics.thumbs_up_ratio,
            'thumbs_up_ratio_se': feedback_metrics.thumbs_up_ratio_se,
            'repetition': feedback_metrics.repetition_score,
            'total_feedback_count': feedback_metrics.total_feedback_count,
            'user_writing_speed': feedback_metrics.user_writing_speed,
        }
    return metrics




def _get_processed_leaderboard(df):
    # maintain backwards compatibility with model_name field
    df['model_name'] = df['model_name'].fillna(df['submission_id'])
    df = _format_leaderboard_date(df)
    df = _filter_submissions_with_few_feedback(df)
    df = df.reset_index(drop=True)
    df = _add_overall_rank(df)
    return df


def _format_leaderboard_date(df):
    df['timestamp'] = df.apply(lambda x: datetime.fromisoformat(x['timestamp']), axis=1)
    df['date'] = df['timestamp'].dt.date
    df.drop(['timestamp'], axis=1, inplace=True)
    return df

def _filter_submissions_with_few_feedback(df):
    filtered_df = df[df.total_feedback_count >= PUBLIC_LEADERBOARD_MINIMUM_FEEDBACK_COUNT]
    return filtered_df


while True:
    try:
        df = display_leaderboard(regenerate=True, detailed=False)
        df = _filter_submissions_with_few_feedback(df)
        df = _add_overall_rank(df)
        df = df[LEADERBOARD_DISPLAY_COLS]
        df['last_updated'] = time.time()
        df.to_csv('db.csv', index=False)
    except KeyboardInterrupt:
        print('interrupted!')
        break
    except:
        continue