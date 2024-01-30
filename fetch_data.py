import multiprocessing
import time

import chaiverse as chai
import numpy as np
from chaiverse import constants
from chaiverse.constants import COMPETITION_TYPE_CONFIGURATION
from chaiverse.metrics.leaderboard_formatter import _get_ranked_leaderboard, _get_formatted_leaderboard
from chaiverse.utils import *
import signal

DEFAULT_MAX_WORKERS = 20
LEADERBOARD_DISPLAY_COLS = COMPETITION_TYPE_CONFIGURATION['default']['output_columns'] + ['total_feedback_count']
LEADERBOARD_DISPLAY_COLS_PRIVATE = COMPETITION_TYPE_CONFIGURATION['submission_closed_feedback_round_robin'][
                                       'output_columns'] + ['total_feedback_count']
def get_display_leaderboard(df, detailed, competition_type):
    competition_configuration = constants.COMPETITION_TYPE_CONFIGURATION[competition_type]
    sort_params = competition_configuration['sort_params']
    output_columns = competition_configuration['output_columns']

    df = _get_ranked_leaderboard(df, sort_params)
    df = _get_formatted_leaderboard(df)
    df = df if detailed else df[output_columns]
    df.index = np.arange(1, len(df) + 1)
    return df


class TimeoutException(Exception):
    pass


def timeout(timeout_time, default):
    def timeout_function(f):
        def f2(*args):
            def timeout_handler(signum, frame):
                raise TimeoutException()

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_time)  # triger alarm in timeout_time seconds
            try:
                retval = f()
            except TimeoutException:
                return default
            finally:
                signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)
            return retval

        return f2

    return timeout_function


@timeout(1800, 'a')
def fetch_lb():
    global t
    if time.time() - t > 3600:
        t = time.time()
        os.system('rm -rf  /root/.chai-guanaco/cache')
    df = chai.get_leaderboard()
    df = get_display_leaderboard(df, detailed=True, competition_type='default')

    df = df[LEADERBOARD_DISPLAY_COLS]
    df['last_updated'] = time.time()
    df.to_csv('db.csv', index=False)

    # df = chai.display_competition_leaderboard()
    # df = df[LEADERBOARD_DISPLAY_COLS_PRIVATE]
    # df['overall_rank'] = df['thumbs_up_ratio'].rank(ascending=False).astype(int)
    # df = df.sort_values('overall_rank')
    # df.to_csv('db_private.csv', index=False)


if __name__ == '__main__':
    t = time.time()
    while True:
        try:
            p = multiprocessing.Process(target=fetch_lb)
            p.start()

            # Wait for 1 hour or until process finishes
            p.join(3600)

            # If thread is still active
            if p.is_alive():
                print("hanging... let's kill it.")

                # Terminate - may not work if process is stuck for good
                # p.terminate()
                # OR Kill - will work for sure, no chance for process to finish nicely however
                p.kill()

                p.join()
        except KeyboardInterrupt:
            print('interrupted!')
            break
        except Exception as e:
            print('==============')
            print(e)
            continue
