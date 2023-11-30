import numpy as np
from chai_guanaco.utils import *
from chai_guanaco.metrics import _get_formatted_leaderboard, _get_processed_leaderboard, _pprint_leaderboard, get_leaderboard, _filter_submissions_with_few_feedback
import time

LEADERBOARD_ENDPOINT = "/leaderboard"
PUBLIC_LEADERBOARD_MINIMUM_FEEDBACK_COUNT = 150
DEFAULT_MAX_WORKERS = 20
LEADERBOARD_DISPLAY_COLS = [
    'developer_uid',
    'submission_id',
    'model_repo',
    'status',
    'is_custom_reward',
    'thumbs_up_ratio',
    'user_writing_speed',
    'repetition',
    'safety_score',
    'total_feedback_count',
    'overall_rank',
]


def display_leaderboard(
        developer_key=None,
        regenerate=False,
        detailed=False,
        max_workers=DEFAULT_MAX_WORKERS
):
    df = get_leaderboard(max_workers=max_workers, developer_key=developer_key)
    df = _get_processed_leaderboard(df, detailed)
    df = _get_formatted_leaderboard(df, detailed)
    _pprint_leaderboard(df)
    return df


def _add_overall_rank(df):
    thumbs_up_rank = df['thumbs_up_ratio'].rank(ascending=False)
    writing_speed_rank = df['user_writing_speed'].rank(ascending=True)
    df['overall_score'] = np.mean([writing_speed_rank, thumbs_up_rank], axis=0)
    df['overall_rank'] = df.overall_score
    df = df.sort_values('overall_rank').reset_index(drop=True)
    return df

while True:
    try:
        os.system('rm -rf  /root/.chai-guanaco/cache')
        df = display_leaderboard(regenerate=True, detailed=True)
        df = _filter_submissions_with_few_feedback(df)
        df = _add_overall_rank(df)
        df = df[LEADERBOARD_DISPLAY_COLS]
        df['last_updated'] = time.time()
        df.to_csv('db.csv', index=False)

    except KeyboardInterrupt:
        print('interrupted!')
        break
    except Exception as e:
        print(e)
        continue