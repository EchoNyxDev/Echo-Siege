RANKING_QUERIES = {
    "paginas": (
        "Mais Páginas Perdidas",
        """
        SELECT user_id, paginas
        FROM biblioteca_players
        ORDER BY paginas DESC, total_acertos DESC
        LIMIT 10
        """,
        "Páginas Perdidas",
    ),
    "acertos": (
        "Mais Acertos",
        """
        SELECT user_id, total_acertos
        FROM biblioteca_players
        ORDER BY total_acertos DESC, maior_combo DESC
        LIMIT 10
        """,
        "acertos",
    ),
    "combo": (
        "Maiores Combos",
        """
        SELECT user_id, maior_combo
        FROM biblioteca_players
        ORDER BY maior_combo DESC, total_acertos DESC
        LIMIT 10
        """,
        "combo",
    ),
    "precisao": (
        "Melhor Precisão",
        """
        SELECT user_id,
               CASE WHEN total_perguntas > 0 THEN ROUND(total_acertos * 100.0 / total_perguntas, 1) ELSE 0 END AS precisao
        FROM biblioteca_players
        WHERE total_perguntas >= 20
        ORDER BY precisao DESC, total_acertos DESC
        LIMIT 10
        """,
        "% de precisão",
    ),
}


def ranking_categories():
    return ", ".join(f"`{key}`" for key in RANKING_QUERIES)


def fetch_ranking(cursor, category):
    category = str(category or "paginas").lower()
    if category not in RANKING_QUERIES:
        category = "paginas"
    title, query, unit = RANKING_QUERIES[category]
    cursor.execute(query)
    return category, title, unit, cursor.fetchall()
