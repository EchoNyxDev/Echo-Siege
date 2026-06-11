import sqlite3

MAX_HERO_LEVEL = 100
MAX_PLAYER_LEVEL = 100

def calcular_level_up(nivel_atual, xp_atual, xp_ganho, fator, max_lvl):
    """Calcula quantos níveis subiu e qual o XP que sobrou"""
    xp = xp_atual + xp_ganho
    lvl = nivel_atual
    niveis_subidos = 0
    
    while xp >= (lvl * fator) and lvl < max_lvl:
        xp -= (lvl * fator)
        lvl += 1
        niveis_subidos += 1
        
    if lvl >= max_lvl:
        lvl = max_lvl
        xp = 0 # Capado no máximo
        
    return niveis_subidos, lvl, xp

def dar_xp_jogador(cursor, user_id, xp_ganho):
    """
    Dá XP para a conta do jogador. Curva de evolução mais lenta (fator 500).
    Ex: Lvl 1 para 2 precisa de 500 XP.
    """
    cursor.execute("SELECT level, xp FROM players WHERE user_id = ?", (str(user_id),))
    data = cursor.fetchone()
    if not data: return 0, 0
    
    lvl, xp = data
    niveis_subidos, novo_lvl, novo_xp = calcular_level_up(lvl, xp, xp_ganho, 500, MAX_PLAYER_LEVEL)
    
    cursor.execute("UPDATE players SET level = ?, xp = ? WHERE user_id = ?", (novo_lvl, novo_xp, str(user_id)))
    return niveis_subidos, novo_lvl

def dar_xp_heroi(cursor, hero_db_id, xp_ganho):
    """
    Dá XP para o herói. Curva de evolução normal (fator 100).
    Ex: Lvl 1 para 2 precisa de 100 XP.
    """
    cursor.execute("SELECT level, xp FROM heroes WHERE id = ?", (int(hero_db_id),))
    data = cursor.fetchone()
    if not data: return 0, 0
    
    lvl, xp = data
    niveis_subidos, novo_lvl, novo_xp = calcular_level_up(lvl, xp, xp_ganho, 100, MAX_HERO_LEVEL)
    
    cursor.execute("UPDATE heroes SET level = ?, xp = ? WHERE id = ?", (novo_lvl, novo_xp, int(hero_db_id)))
    return niveis_subidos, novo_lvl