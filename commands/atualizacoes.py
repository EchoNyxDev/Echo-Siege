import os
import re
import sqlite3
import sys

import discord
from discord.ext import commands

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.patch_notes import PATCH_NOTES, UPDATE_THUMB_URL
except Exception:
    PATCH_NOTES = []
    UPDATE_THUMB_URL = ""

ADM_USERS = {657990219689099264, 768671545790693437}
DEFAULT_THUMB = "https://cdn.discordapp.com/attachments/1493317042760056987/1511161459168514058/TutoriUAU.png"
RECENT_PATCH_LIMIT = 10


def ensure_settings(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_settings(
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)


def get_setting(cursor, key, default=""):
    try:
        ensure_settings(cursor)
        cursor.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row and row[0] else default
    except sqlite3.OperationalError:
        return default


def set_setting(cursor, key, value):
    ensure_settings(cursor)
    cursor.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))


def patch_number(patch):
    candidates = [patch.get("id", ""), patch.get("title", "")]
    for candidate in candidates:
        match = re.search(r"(?:patch[_\s-]*)(\d+)", str(candidate), re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0


class AtualizacoesView(discord.ui.View):
    def __init__(self, user: discord.User, embeds):
        super().__init__(timeout=180)
        self.user = user
        self.embeds = embeds
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_btn.disabled = self.page == 0
        self.next_btn.disabled = self.page >= len(self.embeds) - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Essa atualização foi aberta por outra pessoa. O patch note também tem privacidade, aparentemente.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Patch Anterior", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Próximo Patch", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class Atualizacoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_settings(cursor)
        conn.commit()
        conn.close()

    def _thumb(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        thumb = get_setting(cursor, "updates_thumb", UPDATE_THUMB_URL or DEFAULT_THUMB)
        conn.close()
        return thumb or DEFAULT_THUMB

    def _ordered_notes(self):
        notes = PATCH_NOTES or [{
            "id": "patch_0",
            "title": "Patch Notes",
            "subtitle": "TutoriUAU: ainda não escreveram as notas. Clássico.",
            "rows": [("Sem dados", "Edite `data/patch_notes.py` para adicionar páginas.")],
        }]
        return sorted(notes, key=patch_number, reverse=True)

    def _embeds(self, notes):
        thumb = self._thumb()
        embeds = []
        for idx, patch in enumerate(notes, start=1):
            lines = [f"**{name}** | {text}" for name, text in patch.get("rows", [])]
            comment = patch.get("footer") or patch.get("comment") or "Edite data/patch_notes.py para adicionar novos patches."
            number = patch_number(patch)
            embed = discord.Embed(
                title=patch.get("title", f"Patch {idx}"),
                description=patch.get("subtitle", "Resumo do TutoriUAU, com 30% mais julgamento do que o necessário."),
                color=discord.Color.blurple(),
            )
            embed.add_field(name="Tabela do Patch", value="\n".join(lines)[:1024] or "Nada listado.", inline=False)
            embed.set_thumbnail(url=thumb)
            patch_label = f"Patch {number}" if number else "Patch sem número"
            embed.set_footer(text=f"TutoriUAU • Página {idx}/{len(notes)} • {patch_label} • {comment}")
            embeds.append(embed)
        return embeds

    @commands.command(name="atualiza", aliases=["atualizacao", "atualização", "atualizacoes", "atualizações", "updates", "patch", "patchnotes"])
    async def atualizacao_cmd(self, ctx, numero_patch: int = None):
        ordered_notes = self._ordered_notes()
        if numero_patch is not None:
            selected = next(
                (patch for patch in ordered_notes if patch_number(patch) == numero_patch),
                None,
            )
            if not selected:
                return await ctx.send(
                    f"Não encontrei o **Patch {numero_patch}**. "
                    "TutoriUAU: ou ele ainda não existe, ou foi levado pelo temido departamento de documentação."
                )
            embed = self._embeds([selected])[0]
            return await ctx.send(embed=embed)

        recent_notes = ordered_notes[:RECENT_PATCH_LIMIT]
        embeds = self._embeds(recent_notes)
        view = AtualizacoesView(ctx.author, embeds) if len(embeds) > 1 else None
        await ctx.send(embed=embeds[0], view=view)

    @commands.command(name="atualiza_thumb", aliases=["atualizacao_thumb", "atualização_thumb", "patchthumb", "updatethumb"])
    async def atualizacao_thumb_cmd(self, ctx, *, url: str = None):
        if ctx.author.id not in ADM_USERS:
            return await ctx.send("Apenas ADM pode trocar a thumb das atualizações. O TutoriUAU protege a decoração.")
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return await ctx.send("Use `echo atualiza_thumb <url da imagem>`.")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        set_setting(cursor, "updates_thumb", url.strip()[:500])
        conn.commit()
        conn.close()
        await ctx.send("Thumb das atualizações atualizada. O mural de patch agora tem roupa nova.")


async def setup(bot):
    await bot.add_cog(Atualizacoes(bot))
