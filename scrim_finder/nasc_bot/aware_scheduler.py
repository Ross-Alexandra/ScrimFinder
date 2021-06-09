import datetime
import schedule
from typing import Union
import pytz

class AwareJob(schedule.Job):

    def aware_now(self):
        timezone = getattr(self, "timezone", None)

        if timezone:
            aware_now = datetime.datetime.now().astimezone(pytz.timezone(self.timezone))
        else:
            aware_now = datetime.datetime.now()
        return aware_now.replace(tzinfo=None)

    def at(self, time_str: str, timezone: str):
        self = super().at(time_str)

        self.timezone = timezone
        return self

    def until(
        self,
        until_time: Union[datetime.datetime, datetime.timedelta, datetime.time, str],
    ):
        """
        Schedule job to run until the specified moment.

        The job is canceled whenever the next run is calculated and it turns out the
        next run is after the until_time. The job is also canceled right before it runs,
        if the current time is after until_time. This latter case can happen when the
        the job was scheduled to run before until_time, but runs after until_time.

        If until_time is a moment in the past, ScheduleValueError is thrown.

        :param until_time: A moment in the future representing the latest time a job can
           be run. If only a time is supplied, the date is set to today.
           The following formats are accepted:

           - datetime.datetime
           -  datetime.timedelta
           - datetime.time
           - String in one of the following formats: "%Y-%m-%d %H:%M:%S",
             "%Y-%m-%d %H:%M", "%Y-%m-%d", "%H:%M:%S", "%H:%M"
             as defined by strptime() behaviour. If an invalid string format is passed,
             ScheduleValueError is thrown.

        :return: The invoked job instance
        """

        if isinstance(until_time, datetime.datetime):
            self.cancel_after = until_time
        elif isinstance(until_time, datetime.timedelta):
            self.cancel_after = self.aware_now() + until_time
        elif isinstance(until_time, datetime.time):
            self.cancel_after = datetime.datetime.combine(
                self.aware_now(), until_time
            )
        elif isinstance(until_time, str):
            cancel_after = self._decode_datetimestr(
                until_time,
                [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%d",
                    "%H:%M:%S",
                    "%H:%M",
                ],
            )
            if cancel_after is None:
                raise schedule.ScheduleValueError("Invalid string format for until()")
            if "-" not in until_time:
                # the until_time is a time-only format. Set the date to today
                now = self.aware_now()
                cancel_after = cancel_after.replace(
                    year=now.year, month=now.month, day=now.day
                )
            self.cancel_after = cancel_after
        else:
            raise TypeError(
                "until() takes a string, datetime.datetime, datetime.timedelta, "
                "datetime.time parameter"
            )
        if self.cancel_after < self.aware_now():
            raise schedule.ScheduleValueError(
                "Cannot schedule a job to run until a time in the past"
            )
        return self

    def run(self):
        """
        Run the job and immediately reschedule it.
        If the job's deadline is reached (configured using .until()), the job is not
        run and CancelJob is returned immediately. If the next scheduled run exceeds
        the job's deadline, CancelJob is returned after the execution. In this latter
        case CancelJob takes priority over any other returned value.

        :return: The return value returned by the `job_func`, or CancelJob if the job's
                 deadline is reached.

        """
        if self._is_overdue(self.aware_now()):
            schedule.logger.debug("Cancelling job %s", self)
            return schedule.CancelJob

        schedule.logger.debug("Running job %s", self)
        ret = self.job_func()
        self.last_run = self.aware_now()
        self._schedule_next_run()

        if self._is_overdue(self.next_run):
            schedule.logger.debug("Cancelling job %s", self)
            return schedule.CancelJob
        return ret

    def _schedule_next_run(self) -> None:
        """
        Compute the instant when this job should run next.
        """
        if self.unit not in ("seconds", "minutes", "hours", "days", "weeks"):
            raise schedule.ScheduleValueError(
                "Invalid unit (valid units are `seconds`, `minutes`, `hours`, "
                "`days`, and `weeks`)"
            )

        if self.latest is not None:
            if not (self.latest >= self.interval):
                raise schedule.ScheduleError("`latest` is greater than `interval`")
            interval = schedule.random.randint(self.interval, self.latest)
        else:
            interval = self.interval

        self.period = datetime.timedelta(**{self.unit: interval})
        self.next_run = self.aware_now() + self.period
        if self.start_day is not None:
            if self.unit != "weeks":
                raise schedule.ScheduleValueError("`unit` should be 'weeks'")
            weekdays = (
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            )
            if self.start_day not in weekdays:
                raise schedule.ScheduleValueError(
                    "Invalid start day (valid start days are {})".format(weekdays)
                )
            weekday = weekdays.index(self.start_day)
            days_ahead = weekday - self.next_run.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            self.next_run += datetime.timedelta(days_ahead) - self.period
        if self.at_time is not None:
            if self.unit not in ("days", "hours", "minutes") and self.start_day is None:
                raise schedule.ScheduleValueError("Invalid unit without specifying start day")
            kwargs = {"second": self.at_time.second, "microsecond": 0}
            if self.unit == "days" or self.start_day is not None:
                kwargs["hour"] = self.at_time.hour
            if self.unit in ["days", "hours"] or self.start_day is not None:
                kwargs["minute"] = self.at_time.minute
            self.next_run = self.next_run.replace(**kwargs)  # type: ignore
            # Make sure we run at the specified time *today* (or *this hour*)
            # as well. This accounts for when a job takes so long it finished
            # in the next period.
            if not self.last_run or (self.next_run - self.last_run) > self.period:
                now = self.aware_now()
                if (
                    self.unit == "days"
                    and self.at_time > now.time()
                    and self.interval == 1
                ):
                    self.next_run = self.next_run - datetime.timedelta(days=1)
                elif self.unit == "hours" and (
                    self.at_time.minute > now.minute
                    or (
                        self.at_time.minute == now.minute
                        and self.at_time.second > now.second
                    )
                ):
                    self.next_run = self.next_run - datetime.timedelta(hours=1)
                elif self.unit == "minutes" and self.at_time.second > now.second:
                    self.next_run = self.next_run - datetime.timedelta(minutes=1)
        if self.start_day is not None and self.at_time is not None:
            # Let's see if we will still make that time we specified today
            if (self.next_run - self.aware_now()).days >= 7:
                self.next_run -= self.period

    @property
    def should_run(self) -> bool:
        super().should_run

        return self.aware_now() >= self.next_run

class AwareScheduler(schedule.Scheduler):
    def every(self, interval: int = 1) -> AwareJob:
        """
        Schedule a new periodic aware job.

        :param interval: A quantity of a certain time unit
        :return: An unconfigured :class:`Job <Job>`
        """
        job = AwareJob(interval, self)
        return job

schedule.default_scheduler = AwareScheduler()
