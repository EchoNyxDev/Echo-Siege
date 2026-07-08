import sqlite3
import random

def conceder_ouro_escalavel(cursor, user_id, base_gold, player_level, guild_id=None, extra_mult=1.0):
    """
    Motor centralizado para cálculo e injeção de Ouro em Wolford.
    Leva em consideração o nível do jogador, variação de sorte (RNG),
    multiplicadores de missão, estado da cidade e buffs ativos (Pergaminhos).
    """
    
    # 1. Escalonamento por Nível (Late Game Viável)
    # A cada nível do jogador, o valor base do ouro recebe um bônus (+15 por lvl)
    ouro_escalonado = base_gold + (player_level * 15)
    
    # 2. Variação Aleatória (RNG de 90% a 115%)
    # Dá a sensação de que cada monstro tem uma quantia diferente no bolso
    ouro_base_random = int(ouro_escalonado * random.uniform(0.9, 1.15))
    
    # 3. Multiplicador Direto (Ex: Bosses dão 2.0x, Minions 1.0x)
    ouro_parcial = int(ouro_base_random * extra_mult)
    
    # 4. Multiplicadores do Banco de Dados (Cidade e Buffs do Jogador)
    mult_final = 1.0
    
    # Checa Buff de Ouro (Ex: Pergaminhos de XP/Gold da Loja)
    try:
        cursor.execute("SELECT buff_gold FROM players WHERE user_id = ?", (str(user_id),))
        p_data = cursor.fetchone()
        if p_data and p_data[0] and p_data[0] > 0:
            mult_final += 0.25  # +25% garantido pelo pergaminho
            # Consome 1 carga do buff imediatamente após calcular
            cursor.execute("UPDATE players SET buff_gold = buff_gold - 1 WHERE user_id = ?", (str(user_id),))
    except sqlite3.OperationalError:
        pass # Ignora silenciosamente se a coluna buff_gold ainda não existir
        
    # Checa Prosperidade e Moral da Cidade (se um Guild ID for fornecido)
    if guild_id:
        try:
            cursor.execute("SELECT moral, prosperidade FROM cidades WHERE guild_id = ?", (str(guild_id),))
            city = cursor.fetchone()
            if not city:
                # Fallback para a cidade global se o servidor não tiver cidade própria
                cursor.execute("SELECT moral, prosperidade FROM city_stats WHERE id = 1")
                city = cursor.fetchone()
        except sqlite3.OperationalError:
            cursor.execute("SELECT moral, prosperidade FROM city_stats WHERE id = 1")
            city = cursor.fetchone()
            
        if city:
            moral, prosp = city
            # Bônus de Moral
            if moral > 70: mult_final += 0.10
            elif moral <= 25: mult_final -= 0.10
            
            # Bônus de Prosperidade (Loja)
            if prosp >= 100: mult_final += 0.20
            elif prosp >= 50: mult_final += 0.10

    # 5. Cálculo Final e Arredondamento
    ouro_final = max(1, int(ouro_parcial * mult_final))
    
    # 6. Salva o Ouro na Conta do Jogador
    cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (ouro_final, str(user_id)))
    
    return ouro_final