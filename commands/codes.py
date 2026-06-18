import discord
from discord.ext import commands
import os
import re
import sqlite3
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.equipamentos import EQUIPAMENTOS
    from utils.codes_storage import connect_codes_db, init_codes_db
except ModuleNotFoundError:
    HEROES = {}
    EQUIPAMENTOS = {}
    def connect_codes_db():
        # Adicionado timeout de 20s para evitar locks em picos de uso
        return sqlite3.connect("players.db", timeout=20.0)
    def init_codes_db():
        pass

TUTOR_THUMB = "https://cdn.discordapp.com/attachments/1493317042760056987/1511161459168514058/TutoriUAU.png"
CODES_PER_PAGE = 5
CODES_COMMENTS = [
    "TutoriUAU: code grátis é o tipo de economia que até eu consigo defender.",
    "TutoriUAU: leia o nome antes de resgatar. Sim, este aviso precisou existir.",
    "TutoriUAU: cada jogador usa cada code uma vez. Criatividade fiscal não conta.",
    "TutoriUAU: se o code falhar, confira as letras antes de abrir uma investigação internacional.",
]

class CodesView(discord.ui.View):
    def __init__(self, user, embeds, start_page=0):
        super().__init__(timeout=180)
        self.user = user
        self.embeds = embeds
        self.page = max(0, min(start_page, len(embeds) - 1))
        self._update_buttons()

    def _update_buttons(self):
        self.previous.disabled = self.page <= 0
        self.next.disabled = self.page >= len(self.embeds) - 1

    async def interaction_check(self, interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "Essa lista de codes foi aberta por outra pessoa. Use `echo codes` e ganhe sua própria papelada.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction, button):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Próxima", style=discord.ButtonStyle.primary)
    async def next(self, interaction, button):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class Codes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._inicializar_banco()

    def _inicializar_banco(self):
        """Inicializa o banco de dados se ele ainda nao existir."""
        conn = connect_codes_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS codes (
                code TEXT PRIMARY KEY,
                recompensa TEXT NOT NULL,
                created_at INTEGER DEFAULT 0,
                expires_at INTEGER DEFAULT 0
            )
        """)
        cursor.execute("PRAGMA table_info(codes)")
        code_columns = {row[1] for row in cursor.fetchall()}
        
        if "created_at" not in code_columns:
            cursor.execute("ALTER TABLE codes ADD COLUMN created_at INTEGER DEFAULT 0")
        if "expires_at" not in code_columns:
            cursor.execute("ALTER TABLE codes ADD COLUMN expires_at INTEGER DEFAULT 0")
            
        # Correção do Bug de Desaparecimento (Transforma os antigos NULL em 0)
        cursor.execute("UPDATE codes SET expires_at = 0 WHERE expires_at IS NULL")
            
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_redemptions (
                code TEXT NOT NULL,
                user_id TEXT NOT NULL,
                redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (code, user_id)
            )
        """)
        conn.commit()
        conn.close()

    def _descricao_token(self, recompensa):
        recompensa_upper = recompensa.upper()

        if re.fullmatch(r"G\d+", recompensa_upper):
            return f"{int(recompensa_upper[1:])} Gold"

        if re.fullmatch(r"T\d+", recompensa_upper):
            return f"{int(recompensa_upper[1:])} Summon Ticket(s)"

        recompensa_id = recompensa.lower().replace(" ", "_")
        if recompensa_id in HEROES:
            return HEROES[recompensa_id].get("nome", recompensa_id)

        return EQUIPAMENTOS.get(recompensa_id, {}).get("nome", recompensa_id.replace("_", " ").title())

    def _descricao_recompensa(self, recompensa):
        return " + ".join(self._descricao_token(token) for token in str(recompensa or "").split())

    def _listar_codes(self, user_id):
        conn = connect_codes_db()
        cursor = conn.cursor()
        try:
            # Bug de Desaparecimento corrigido no COALESCE
            cursor.execute(
                """
                SELECT
                    c.code,
                    c.recompensa,
                    c.expires_at,
                    COUNT(r.user_id) AS total_resgates,
                    MAX(CASE WHEN r.user_id = ? THEN 1 ELSE 0 END) AS resgatado_pelo_usuario
                FROM codes c
                LEFT JOIN code_redemptions r ON r.code = c.code
                WHERE COALESCE(c.expires_at, 0) = 0 OR c.expires_at > ?
                GROUP BY c.code, c.recompensa, c.expires_at
                ORDER BY c.code ASC
                """,
                (str(user_id), int(time.time())),
            )
            return cursor.fetchall()
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()

    def _codes_embeds(self, user, rows):
        total_pages = max(1, (len(rows) + CODES_PER_PAGE - 1) // CODES_PER_PAGE)
        available = sum(1 for row in rows if not row[4])
        redeemed = len(rows) - available
        embeds = []
        for page_index in range(total_pages):
            start = page_index * CODES_PER_PAGE
            page_rows = rows[start:start + CODES_PER_PAGE]
            lines = []
            for code, reward, expires_at, total_redemptions, user_redeemed in page_rows:
                status = "Já resgatado" if user_redeemed else "Disponível"
                marker = "✅" if user_redeemed else "🎁"
                code_label = str(code)[:48]
                reward_label = self._descricao_recompensa(reward)[:90]
                if expires_at:
                    remaining = max(0, int(expires_at) - int(time.time()))
                    days, remainder = divmod(remaining, 86400)
                    hours = remainder // 3600
                    validity = f"Expira em: **{days}d {hours}h**"
                else:
                    validity = "Validade: **permanente**"
                lines.append(
                    f"{marker} **`{code_label}`**\n"
                    f"Recompensa: **{reward_label}**\n"
                    f"{validity}\n"
                    f"Seu status: **{status}** | Resgates globais: **{total_redemptions}**"
                )

            comment = CODES_COMMENTS[page_index % len(CODES_COMMENTS)]
            embed = discord.Embed(
                title="Codes Disponíveis",
                description=(
                    f"{user.mention}, use `echo code <código>` para resgatar.\n"
                    f"Disponíveis para você: **{available}** | Já resgatados: **{redeemed}**"
                ),
                color=discord.Color.gold(),
            )
            embed.add_field(
                name=f"Catálogo de Codes • Página {page_index + 1}/{total_pages}",
                value="\n\n".join(lines) or "Nenhum code cadastrado no momento.",
                inline=False,
            )
            embed.set_thumbnail(url=TUTOR_THUMB)
            embed.set_footer(text=f"{comment} Página {page_index + 1} arquivada sem perder nenhum papel.")
            embeds.append(embed)
        return embeds

    def _aplicar_recompensa(self, user_id, recompensa):
        conn = sqlite3.connect("players.db", timeout=20.0)
        cursor = conn.cursor()

        cursor.execute("SELECT user_id FROM players WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return False, "Você ainda não iniciou sua jornada. Use `echo iniciar` antes de resgatar codes."

        try:
            for token in str(recompensa or "").split():
                recompensa_upper = token.upper()
                recompensa_id = token.lower().replace(" ", "_")

                if re.fullmatch(r"G\d+", recompensa_upper):
                    valor = int(recompensa_upper[1:])
                    if valor <= 0:
                        raise ValueError("Esse code tem uma recompensa de Gold inválida.")
                    cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (valor, user_id))

                elif re.fullmatch(r"T\d+", recompensa_upper):
                    valor = int(recompensa_upper[1:])
                    if valor <= 0:
                        raise ValueError("Esse code tem uma recompensa de Ticket inválida.")
                    cursor.execute(
                        "UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?",
                        (valor, user_id),
                    )

                elif recompensa_id in HEROES:
                    cursor.execute(
                        "INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)",
                        (user_id, recompensa_id, HEROES[recompensa_id].get("raridade", 1)),
                    )

                else:
                    cursor.execute(
                        "SELECT id FROM inventory WHERE user_id = ? AND item_name = ?",
                        (user_id, recompensa_id),
                    )
                    item_existe = cursor.fetchone()
                    if item_existe:
                        cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE id = ?", (item_existe[0],))
                    else:
                        cursor.execute(
                            "INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)",
                            (user_id, recompensa_id),
                        )
            conn.commit()
        except (sqlite3.Error, ValueError) as exc:
            conn.rollback()
            conn.close()
            return False, str(exc)

        conn.close()
        return True, self._descricao_recompensa(recompensa)

    @commands.command(name="code")
    async def resgatar_code(self, ctx, nome_do_code: str = None):
        """Comando para resgatar codigos: echo code <nome>."""
        if not nome_do_code:
            return await ctx.send(
                "Use `echo code <nome-do-code>` para resgatar ou `echo codes` para consultar os disponíveis. "
                "TutoriUAU: organização, finalmente."
            )

        codigo = nome_do_code.upper()
        conn = connect_codes_db()
        cursor = conn.cursor()

        cursor.execute("SELECT recompensa, expires_at FROM codes WHERE code = ?", (codigo,))
        resultado = cursor.fetchone()

        if not resultado:
            conn.close()
            return await ctx.send(f"❌ O código **{nome_do_code}** é inválido.")

        recompensa, expires_at = resultado
        if expires_at and int(expires_at) <= int(time.time()):
            conn.close()
            return await ctx.send(
                f"❌ O código **{nome_do_code}** expirou. TutoriUAU tentou negociar com o calendário e perdeu."
            )

        # 1. Inserimos o resgate PRIMEIRO para travar a corrida (Race Condition)
        try:
            cursor.execute(
                "INSERT INTO code_redemptions (code, user_id) VALUES (?, ?)",
                (codigo, str(ctx.author.id)),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return await ctx.send(f"❌ Você já resgatou o código **{nome_do_code}**.")

        # 2. Fechamos a conexão Imediatamente para liberar o banco e evitar Locks!
        conn.close()

        # 3. Agora aplicamos a recompensa com o banco livre
        sucesso, mensagem = self._aplicar_recompensa(str(ctx.author.id), recompensa)
        
        # 4. Se a recompensa falhar, devolvemos o uso do code ao jogador
        if not sucesso:
            conn = connect_codes_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM code_redemptions WHERE code = ? AND user_id = ?", (codigo, str(ctx.author.id)))
            conn.commit()
            conn.close()
            return await ctx.send(f"❌ Falha no resgate: {mensagem}")

        await ctx.send(f"✅ Código resgatado! Você recebeu: **{mensagem}**")

    @commands.command(name="codes", aliases=["codigos", "códigos", "cupons"])
    async def listar_codes(self, ctx, pagina: int = 1):
        rows = self._listar_codes(ctx.author.id)
        if not rows:
            return await ctx.send(
                "Nenhum code disponível agora. TutoriUAU: o cofre está vazio, mas pelo menos está catalogado."
            )

        embeds = self._codes_embeds(ctx.author, rows)
        requested_page = max(1, pagina)
        if requested_page > len(embeds):
            return await ctx.send(
                f"A lista só possui **{len(embeds)} página(s)**. "
                "TutoriUAU: você encontrou conteúdo futuro; volte quando o orçamento permitir."
            )
        start_page = requested_page - 1
        view = CodesView(ctx.author, embeds, start_page) if len(embeds) > 1 else None
        await ctx.send(embed=embeds[start_page], view=view)


async def setup(bot):
    await bot.add_cog(Codes(bot))