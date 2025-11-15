from celery import shared_task

from app.decorators.channel_decorator import with_channel_service
from app.services.channel_service import ChannelService


@shared_task(name="parse_channels_cycle")
@with_channel_service
def parse_channels_cycle_task(channel_service: ChannelService = None):
    return channel_service.parse_channels(limit=100, delay=0.1)


@shared_task(name="parse_channel_info")
@with_channel_service
def parse_channel_info_task(channel_link: str, channel_service: ChannelService = None):
    return channel_service.parse_channels(channel_links=[channel_link])
