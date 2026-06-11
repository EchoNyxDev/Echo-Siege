import asyncio

async def type_message(msg, text, speed=0.02):
    """
    Simula digitação editando a mesma mensagem.
    Ideal para cutscenes simples.
    """

    buffer = ""

    for char in text:
        buffer += char
        await msg.edit(content=buffer)
        await asyncio.sleep(speed)