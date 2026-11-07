import ast
from pathlib import Path
import unittest

import discord
from discord.ext import commands

from systems.i18n import (
    COMMAND_TRANSLATIONS,
    _translate_command_snippet,
    canonical_command_token,
    normalize_language,
    register_multilingual_command_aliases,
)


async def _dummy_callback(ctx):
    return None


class I18nTests(unittest.TestCase):
    def test_language_normalization(self):
        self.assertEqual(normalize_language("pt-BR"), "pt")
        self.assertEqual(normalize_language("English"), "en")
        self.assertEqual(normalize_language("Español"), "es")

    def test_command_snippets_are_localized(self):
        self.assertEqual(_translate_command_snippet("`echo perfil`", "en"), "`echo profile`")
        self.assertEqual(_translate_command_snippet("`echo loja comprar`", "es"), "`echo tienda comprar`")

    def test_prefix_aliases_are_registered_recursively(self):
        bot = commands.Bot(command_prefix="echo ", intents=discord.Intents.none())
        profile = commands.Command(_dummy_callback, name="perfil")
        shop = commands.Group(_dummy_callback, name="loja")
        buy = commands.Command(_dummy_callback, name="comprar")
        shop.add_command(buy)
        bot.add_command(profile)
        bot.add_command(shop)

        stats = register_multilingual_command_aliases(bot)

        self.assertIs(bot.get_command("profile"), profile)
        self.assertIs(bot.get_command("shop buy"), buy)
        self.assertIs(bot.get_command("tienda comprar"), buy)
        self.assertGreater(stats["en"], 0)
        self.assertGreater(stats["es"], 0)

    def test_admin_tokens_are_canonicalized(self):
        self.assertEqual(canonical_command_token("start"), "iniciar")
        self.assertEqual(canonical_command_token("comenzar"), "iniciar")
        self.assertEqual(canonical_command_token("jefe"), "boss")
        self.assertEqual(canonical_command_token("calamity"), "calamidade")

    def test_every_declared_command_has_multilingual_vocabulary(self):
        command_names = set()
        commands_dir = Path(__file__).resolve().parents[1] / "commands"
        for path in commands_dir.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for decorator in node.decorator_list:
                    if not isinstance(decorator, ast.Call):
                        continue
                    for keyword in decorator.keywords:
                        if keyword.arg != "name" or not isinstance(keyword.value, ast.Constant):
                            continue
                        if isinstance(keyword.value.value, str):
                            command_names.add(keyword.value.value)

        missing = sorted(
            name for name in command_names
            if canonical_command_token(name) not in COMMAND_TRANSLATIONS
        )
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
