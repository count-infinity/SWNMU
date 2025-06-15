from typeclasses.objects import Object
import json


class EventContext:
    def __init__(self):
        self.cancelled = False


class Event:

    def __init__(
        self,
        event_type: str,
        source: Object,
        target: Object,
        context: EventContext = EventContext(),
        *args,
        **kwargs,
    ):
        self.source = source
        self.target = target
        self.event_type = event_type
        self.pre_event_func = f"at_pre_event"
        self.event_handler_func = f"handle_event"
        self.post_event_func = f"at_post_event"
        self.context = context
        self.history = []
        self.__dict__.update(kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return json.dumps(
            {
                "type": self.event_type,
                "source": self.source.key,
                "target": self.target.key,
                "history": self.history,
            },
            indent=2,
        )


class GlobalEventHandler:
    @classmethod
    def handleEvent(cls, event: Event):
        print("Handling event")

        if pre_handler := getattr(event.source, event.pre_event_func, None):
            pre_handler(event)
        if pre_handler := getattr(event.source.location, event.pre_event_func, None):
            pre_handler(event)
        if pre_handler := getattr(event.target, event.pre_event_func, None):
            pre_handler(event)

        if event_handler := getattr(event.source, event.event_handler_func, None):
            event_handler(event)
        print(f"Location {event.source} - {event.source.location}")
        if event_handler := getattr(event.source.location, event.event_handler_func, None):
            print("Location event handler")
            event_handler(event)
        if event_handler := getattr(event.target, event.event_handler_func, None):
            event_handler(event)

        if post_handler := getattr(event.source, event.post_event_func, None):
            post_handler(event)
        if post_handler := getattr(event.source.location, event.post_event_func, None):
            post_handler(event)
        if post_handler := getattr(event.target, event.post_event_func, None):
            post_handler(event)

        event.source.msg(event)
