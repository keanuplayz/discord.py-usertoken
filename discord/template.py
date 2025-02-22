"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from .utils import parse_time, _get_as_snowflake, _bytes_to_base64_data
from .enums import VoiceRegion
from .guild import Guild

__all__ = (
    'Template',
)


class _FriendlyHttpAttributeErrorHelper:
    __slots__ = ()

    def __getattr__(self, attr):
        raise AttributeError('PartialTemplateState does not support http methods.')


class _PartialTemplateState:
    def __init__(self, *, state):
        self.__state = state
        self.http = _FriendlyHttpAttributeErrorHelper()

    @property
    def is_bot(self):
        return self.__state.is_bot

    @property
    def shard_count(self):
        return self.__state.shard_count

    @property
    def user(self):
        return self.__state.user

    @property
    def self_id(self):
        return self.__state.user.id

    @property
    def member_cache_flags(self):
        return self.__state.member_cache_flags

    def store_emoji(self, guild, packet):
        return None

    def _get_voice_client(self, id):
        return None

    def _get_message(self, id):
        return None

    async def query_members(self, **kwargs):
        return []

    def __getattr__(self, attr):
        raise AttributeError(f'PartialTemplateState does not support {attr!r}.')


class Template:
    """Represents a Discord template.

    .. versionadded:: 1.4

    Attributes
    -----------
    code: :class:`str`
        The template code.
    uses: :class:`int`
        How many times the template has been used.
    name: :class:`str`
        The name of the template.
    description: :class:`str`
        The description of the template.
    creator: :class:`User`
        The creator of the template.
    created_at: :class:`datetime.datetime`
        An aware datetime in UTC representing when the template was created.
    updated_at: :class:`datetime.datetime`
        An aware datetime in UTC representing when the template was last updated.
        This is referred to as "last synced" in the official Discord client.
    source_guild: :class:`Guild`
        The source guild.
    """

    def __init__(self, *, state, data):
        self._state = state
        self._store(data)

    def _store(self, data):
        self.code = data['code']
        self.uses = data['usage_count']
        self.name = data['name']
        self.description = data['description']
        creator_data = data.get('creator')
        self.creator = None if creator_data is None else self._state.store_user(creator_data)

        self.created_at = parse_time(data.get('created_at'))
        self.updated_at = parse_time(data.get('updated_at'))

        id = _get_as_snowflake(data, 'source_guild_id')

        guild = self._state._get_guild(id)

        if guild is None:
            source_serialised = data['serialized_source_guild']
            source_serialised['id'] = id
            state = _PartialTemplateState(state=self._state)
            guild = Guild(data=source_serialised, state=state)
        
        self.source_guild = guild

    def __repr__(self):
        return (
            f'<Template code={self.code!r} uses={self.uses} name={self.name!r}'
            f' creator={self.creator!r} source_guild={self.source_guild!r}>'
        )

    async def create_guild(self, name, region=None, icon=None):
        """|coro|

        Creates a :class:`.Guild` using the template.

        Bot accounts in more than 10 guilds are not allowed to create guilds.

        Parameters
        ----------
        name: :class:`str`
            The name of the guild.
        region: :class:`.VoiceRegion`
            The region for the voice communication server.
            Defaults to :attr:`.VoiceRegion.us_west`.
        icon: :class:`bytes`
            The :term:`py:bytes-like object` representing the icon. See :meth:`.ClientUser.edit`
            for more details on what is expected.

        Raises
        ------
        HTTPException
            Guild creation failed.
        InvalidArgument
            Invalid icon image format given. Must be PNG or JPG.

        Returns
        -------
        :class:`.Guild`
            The guild created. This is not the same guild that is
            added to cache.
        """
        if icon is not None:
            icon = _bytes_to_base64_data(icon)

        region = region or VoiceRegion.us_west
        region_value = region.value

        data = await self._state.http.create_from_template(self.code, name, region_value, icon)
        return Guild(data=data, state=self._state)

    async def sync(self):
        """|coro|

        Sync the template to the guild's current state.

        You must have the :attr:`~Permissions.manage_guild` permission in the
        source guild to do this.

        .. versionadded:: 1.7

        Raises
        -------
        HTTPException
            Editing the template failed.
        Forbidden
            You don't have permissions to edit the template.
        NotFound
            This template does not exist.
        """

        data = await self._state.http.sync_template(self.source_guild.id, self.code)
        self._store(data)

    async def edit(self, **kwargs):
        """|coro|

        Edit the template metadata.

        You must have the :attr:`~Permissions.manage_guild` permission in the
        source guild to do this.

        .. versionadded:: 1.7

        Parameters
        ------------
        name: Optional[:class:`str`]
            The template's new name.
        description: Optional[:class:`str`]
            The template's description.

        Raises
        -------
        HTTPException
            Editing the template failed.
        Forbidden
            You don't have permissions to edit the template.
        NotFound
            This template does not exist.
        """
        data = await self._state.http.edit_template(self.source_guild.id, self.code, kwargs)
        self._store(data)

    async def delete(self):
        """|coro|

        Delete the template.

        You must have the :attr:`~Permissions.manage_guild` permission in the
        source guild to do this.

        .. versionadded:: 1.7

        Raises
        -------
        HTTPException
            Editing the template failed.
        Forbidden
            You don't have permissions to edit the template.
        NotFound
            This template does not exist.
        """
        await self._state.http.delete_template(self.source_guild.id, self.code)
