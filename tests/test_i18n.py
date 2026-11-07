import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import discord
from discord.ext import commands

from systems.i18n import (
    COMMAND_TRANSLATIONS,
    _localize_payload_for_language,
    _language_for_message,
    _translate_command_snippet,
    _translate_uncached,
    build_command_alias_catalog,
    canonical_command_token,
    localized_command_path,
    normalize_language,
    paginate_command_alias_catalog,
    remember_message_language,
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

    def test_help_catalog_comes_from_loaded_commands(self):
        bot = commands.Bot(command_prefix="echo ", intents=discord.Intents.none())
        profile = commands.Command(_dummy_callback, name="perfil")
        shop = commands.Group(_dummy_callback, name="loja")
        buy = commands.Command(_dummy_callback, name="comprar")
        shop.add_command(buy)
        bot.add_command(profile)
        bot.add_command(shop)

        english = build_command_alias_catalog(bot, "en")
        spanish = build_command_alias_catalog(bot, "es")

        self.assertIn("echo perfil -> echo profile", english)
        self.assertIn("echo loja comprar -> echo shop buy", english)
        self.assertIn("echo loja comprar -> echo tienda comprar", spanish)
        self.assertEqual(localized_command_path("guild criar", "en"), "guild create")

        pages = paginate_command_alias_catalog(english, max_field_chars=80, fields_per_page=2)
        self.assertTrue(pages)
        self.assertTrue(all(len("\n".join(field)) <= 80 for page in pages for field in page))

    def test_admin_tokens_are_canonicalized(self):
        self.assertEqual(canonical_command_token("start"), "iniciar")
        self.assertEqual(canonical_command_token("comenzar"), "iniciar")
        self.assertEqual(canonical_command_token("jefe"), "boss")
        self.assertEqual(canonical_command_token("calamity"), "calamidade")

    def test_late_message_edits_remember_the_player_language(self):
        message = SimpleNamespace(id=987654321, guild=None)
        remember_message_language(message, "es")
        self.assertEqual(_language_for_message(message), "es")

    def test_prose_and_command_snippets_translate_together(self):
        def fake_provider(text, target_lang, source_lang="pt"):
            return f"[{target_lang}] {text}"

        with patch("systems.i18n._provider_translate", side_effect=fake_provider):
            english = _translate_uncached("Abra `echo perfil` para continuar.", "en")
            spanish = _translate_uncached("Abra `echo loja comprar` para continuar.", "es")

        self.assertEqual(english, "[en] Abra `echo profile` para continuar.")
        self.assertEqual(spanish, "[es] Abra `echo tienda comprar` para continuar.")

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


class PayloadI18nTests(unittest.IsolatedAsyncioTestCase):
    async def test_content_embed_and_buttons_follow_selected_language(self):
        async def fake_translate(text, target_lang, source_lang="pt"):
            return f"[{target_lang}] {text}"

        for language in ("en", "es"):
            embed = discord.Embed(title="Título", description="Descrição")
            embed.add_field(name="Campo", value="Valor", inline=False)
            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(label="Continuar"))

            with patch("systems.i18n.translate_text", side_effect=fake_translate):
                content, kwargs = await _localize_payload_for_language(
                    language,
                    "Mensagem",
                    {"embed": embed, "view": view},
                )

            self.assertEqual(content, f"[{language}] Mensagem")
            self.assertEqual(kwargs["embed"].title, f"[{language}] Título")
            self.assertEqual(kwargs["embed"].fields[0].value, f"[{language}] Valor")
            self.assertEqual(kwargs["view"].children[0].label, f"[{language}] Continuar")

    async def test_portuguese_payload_is_not_modified(self):
        embed = discord.Embed(title="Título em português")
        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label="Continuar"))

        content, kwargs = await _localize_payload_for_language(
            "pt",
            "Mensagem original",
            {"embed": embed, "view": view},
        )

        self.assertEqual(content, "Mensagem original")
        self.assertIs(kwargs["embed"], embed)
        self.assertEqual(kwargs["view"].children[0].label, "Continuar")


if __name__ == "__main__":
    unittest.main()
