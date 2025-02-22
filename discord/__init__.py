"""
Discord API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Discord API.

:copyright: (c) 2015-present Rapptz
:license: MIT, see LICENSE for more details.

"""

__title__ = 'discord'
__author__ = 'keanucode'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015-present Rapptz'
__version__ = '2.0.0a'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

from collections import namedtuple
import logging

from .partial_emoji import PartialEmoji
from .emoji import Emoji
from .user import User, ClientUser, Profile
from .appinfo import AppInfo
from .client import Client
from .activity import *
from .channel import *
from .guild import *
from .flags import *
from .relationship import Relationship
from .member import Member, VoiceState
from .message import *
from .asset import *
from .errors import *
from .calls import CallMessage, GroupCall
from .permissions import Permissions, PermissionOverwrite
from .role import Role, RoleTags
from .file import File
from .colour import Color, Colour
from .integrations import Integration, IntegrationAccount
from .invite import Invite, PartialInviteChannel, PartialInviteGuild
from .template import Template
from .widget import Widget, WidgetMember, WidgetChannel
from .object import Object
from .reaction import Reaction
from . import utils, opus, abc
from .enums import *
from .embeds import *
from .mentions import *
from .shard import *
from .player import *
from .webhook import *
from .voice_client import *
from .audit_logs import *
from .raw_models import *
from .team import *
from .sticker import *
from .interactions import *

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=2, minor=0, micro=0, releaselevel='alpha', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())
