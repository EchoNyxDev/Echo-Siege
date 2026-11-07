from types import SimpleNamespace
import unittest

import main
from systems.i18n import localized_command_path, register_multilingual_command_aliases


class HelpTranslationCatalogTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        if main.bot.get_cog("Ajuda") is None:
            await main.load_commands()
            register_multilingual_command_aliases(main.bot)
        invasions = main.bot.get_cog("Invasoes")
        if invasions and invasions.invasion_scheduler.is_running():
            invasions.invasion_scheduler.cancel()

    def test_help_and_tutorial_include_english_and_spanish_catalogs(self):
        user = SimpleNamespace(id=123456789, mention="<@123456789>")
        help_pages = main.bot.get_cog("Ajuda").criar_paginas_ajuda(user)
        tutorial_pages = main.bot.get_cog("Tutorial").criar_paginas(user)

        for pages in (help_pages, tutorial_pages):
            rendered = "\n".join(
                str(value)
                for embed in pages
                for value in (
                    embed.title or "",
                    embed.description or "",
                    *(field.value for field in embed.fields),
                )
            )
            self.assertIn("echo perfil -> echo profile", rendered)
            self.assertIn("echo guild criar -> echo gremio crear", rendered)
            self.assertGreater(len(pages), 7)

            for embed in pages:
                self.assertLessEqual(len(embed.title or ""), 256)
                self.assertLessEqual(len(embed.description or ""), 4096)
                self.assertLessEqual(len(embed), 6000)
                self.assertLessEqual(len(embed.fields), 25)
                self.assertTrue(all(len(field.name) <= 256 for field in embed.fields))
                self.assertTrue(all(len(field.value) <= 1024 for field in embed.fields))

    def test_every_localized_command_path_resolves(self):
        unresolved = []
        for command in main.bot.walk_commands():
            for language in ("en", "es"):
                localized = localized_command_path(command, language)
                if main.bot.get_command(localized) is not command:
                    unresolved.append((command.qualified_name, language, localized))
        self.assertEqual(unresolved, [])


if __name__ == "__main__":
    unittest.main()
