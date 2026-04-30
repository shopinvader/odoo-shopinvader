This module provides a way to link FastAPI endpoints to Sale Channels.

It sets a `sale_channel_id` in the request context for endpoints linked to a Sale Channel,
and it auto attach Sale Orders created via these endpoints to the corresponding Sale Channel.
