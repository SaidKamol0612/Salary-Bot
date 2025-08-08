from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


class BotLoader:
    _bot: Bot | None = None

    @classmethod
    def get_bot(cls, token: str, is_html_or_md: bool = True) -> Bot:
        if cls._bot is None:
            cls._bot = Bot(
                token=token,
                default=DefaultBotProperties(
                    parse_mode=(
                        ParseMode.HTML if is_html_or_md else ParseMode.MARKDOWN_V2
                    )
                ),
            )
        return cls._bot

    @staticmethod
    async def set_bot_commands(bot: Bot, new_commands: dict[str, str]):
        commands = []
        for command, desc in new_commands.items():
            commands.append(BotCommand(command=command, description=desc))
        await bot.set_my_commands(commands)
