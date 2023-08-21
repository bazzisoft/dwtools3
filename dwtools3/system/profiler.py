import cProfile
import pstats
import StringIO


def profile_function(fn, sort_by_cumulative_time=True):
    pr = cProfile.Profile()
    pr.enable()
    fn()
    pr.disable()
    s = StringIO.StringIO()
    sortby = "time" if not sort_by_cumulative_time else "cumulative"
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    return s.getvalue()
