import sqlite3
import time

from discord.ext import commands


def init_admin_logs(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS administrative_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            value TEXT,
            admin_id TEXT,
            timestamp INTEGER DEFAULT 0,
            status TEXT DEFAULT 'open',
            resolution TEXT DEFAULT '',
            resolved_by TEXT,
            resolved_at INTEGER DEFAULT 0
        )
    """)
    cursor.execute("PRAGMA table_info(administrative_logs)")
    columns = {row[1] for row in cursor.fetchall()}
    for column, ddl in {
        "status": "TEXT DEFAULT 'open'",
        "resolution": "TEXT DEFAULT ''",
        "resolved_by": "TEXT",
        "resolved_at": "INTEGER DEFAULT 0",
    }.items():
        if column not in columns:
            cursor.execute(f"ALTER TABLE administrative_logs ADD COLUMN {column} {ddl}")


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_admin_logs(cursor)
        conn.commit()
        conn.close()

    @commands.command(name="bug", aliases=["queixa", "reportar", "suporte"])
    async def bug_cmd(self, ctx, *, texto: str = None):
        if not texto or len(texto.strip()) < 5:
            return await ctx.send("Descreva o problema. Exemplo: `echo bug meu ticket desapareceu depois do summon`.")

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_admin_logs(cursor)
        action = "bug_usuario" if (ctx.invoked_with or "").lower() == "bug" else "queixa_usuario"
        cursor.execute(
            """
            INSERT INTO administrative_logs
            (user_id, action, value, admin_id, timestamp, status)
            VALUES (?, ?, ?, NULL, ?, 'open')
            """,
            (str(ctx.author.id), action, texto.strip()[:900], int(time.time())),
        )
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()

        await ctx.send(
            f"{'Bug' if action == 'bug_usuario' else 'Queixa'} registrada como **#{log_id}**. O TutoriUAU colocou num bloquinho digital, "
            "que é quase profissional. Quando a equipe resolver, você receberá a resposta por mensagem direta."
        )


async def setup(bot):
    await bot.add_cog(Logs(bot))
