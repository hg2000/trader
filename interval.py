class Interval:

    m1 = 'm1'
    m5 = 'm5'
    m15 = 'm15'
    h1 = 'h1'
    h4 = 'h4'
    d1 = 'd1'

    @staticmethod
    def get_multiplier(interval):

        if interval == Interval.m5:
            return 1

        if interval == Interval.m15:
            return 3

        if interval == Interval.h1:
            return 12

        if interval == Interval.h4:
            return 48

        if interval == Interval.d1:
            return 96


        raise BaseException('invalid interval %s' % interval)

    @staticmethod
    def get_minutes(interval):

        if interval == Interval.m5:
            return 1

        if interval == Interval.m15:
            return 15

        if interval == Interval.h1:
            return 60

        if interval == Interval.h4:
            return 240

        if interval == Interval.d1:
            return 1440


        raise BaseException('invalid interval %s' % interval)
