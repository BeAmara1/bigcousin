import discord

ACCENT_COLOR = 0x5865F2
SUCCESS_COLOR = 0x57F287
WARNING_COLOR = 0xFEE75C
ERROR_COLOR = 0xED4245
DARK_COLOR = 0x2B2D31

SEPARATOR = "\u2500" * 24


def base_embed(title=None, description=None, color=ACCENT_COLOR):
    embed = discord.Embed(title=title, description=description, color=color)
    return embed


def profile_embed(user_data):
    user = user_data["user"]
    stats = user_data["stats"]

    embed = discord.Embed(
        title=f"{user.username}",
        description=f"Perfil de jogos no BigCousin",
        color=ACCENT_COLOR,
    )

    embed.set_thumbnail(url=user.avatar_url)

    stats_text = (
        f"`🎮` Jogos: **{stats['total_games']}**\n"
        f"`✅` Zerados: **{stats['beaten_count']}**\n"
        f"`⭐` Média: **{stats['avg_rating']:.1f}**" if stats['avg_rating'] else "`⭐` Média: **--**"
    )
    embed.add_field(name="📊 Estatísticas", value=stats_text, inline=False)

    if stats['recent_games']:
        recent = "\n".join(
            f"• **{game.name}** ⭐ {rating.score}"
            for game, rating in stats['recent_games']
        )
        embed.add_field(name="🎮 Jogados Recentemente", value=recent, inline=False)

    if stats['favorites']:
        favs = "\n".join(f"• **{f.game.name}**" for f in stats['favorites'])
        embed.add_field(name="⭐ Favoritos", value=favs, inline=True)

    if stats['backlog_count'] > 0:
        embed.add_field(name="📋 Backlog", value=f"**{stats['backlog_count']}** jogos", inline=True)

    if stats['latest_review']:
        rv = stats['latest_review']
        embed.add_field(
            name=f"💬 Review Recente — {rv.game.name}",
            value=f"\"{rv.text[:200]}{'...' if len(rv.text) > 200 else ''}\"",
            inline=False,
        )

    embed.set_footer(text=f"Membro desde {user.created_at.strftime('%d/%m/%Y')}")
    return embed


def game_list_embed(user, games_page, page, total_pages):
    embed = discord.Embed(
        title=f"Biblioteca de {user.name}",
        description=f"**{len(games_page)} jogos** — Página {page + 1}/{total_pages}",
        color=ACCENT_COLOR,
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    game_lines = []
    for game, rating, in_backlog, is_fav in games_page:
        line = f"**{game.name}**"
        if rating:
            line += f" ⭐ {rating.score}/10"
        flags = []
        if in_backlog:
            flags.append("📋")
        if is_fav:
            flags.append("⭐")
        if flags:
            line += " " + "".join(flags)
        game_lines.append(line)

    embed.description = "\n".join(game_lines) if game_lines else "Nenhum jogo encontrado."
    embed.set_footer(text=f"{len(games_page)} jogos • Página {page + 1}/{total_pages}")
    return embed


def rating_embed(user, game, score):
    embed = discord.Embed(
        title=f"⭐ Avaliação Registrada",
        description=f"**{game.name}** recebeu **{score}/10** de {user.name}",
        color=SUCCESS_COLOR,
    )

    if game.cover_url:
        embed.set_thumbnail(url=game.cover_url)

    return embed


def review_embed(user, game, review_text):
    embed = discord.Embed(
        title=f"💬 Review de {user.name}",
        description=f"**{game.name}**",
        color=ACCENT_COLOR,
    )

    embed.add_field(name="Review", value=f"\"{review_text}\"", inline=False)

    if game.cover_url:
        embed.set_thumbnail(url=game.cover_url)

    embed.set_footer(text=f"Review por {user.name}")
    return embed


def backlog_embed(items, page, total_pages):
    embed = discord.Embed(
        title="📋 Backlog",
        description="Jogos que você planeja jogar:",
        color=WARNING_COLOR,
    )

    if items:
        lines = "\n".join(f"{i + 1}. **{g.name}**" for i, g in enumerate(items))
        embed.add_field(name=f"Página {page + 1}/{total_pages}", value=lines, inline=False)
    else:
        embed.description = "Nenhum jogo no backlog."

    return embed


def addgame_embed(user, game):
    genres_text = ", ".join(game.genres) if game.genres else "N/A"
    platforms_text = ", ".join(game.platforms[:5]) if game.platforms else "N/A"

    embed = discord.Embed(
        title=f"🎮 Jogo Adicionado",
        description=f"**{game.name}** foi adicionado à biblioteca de {user.name}",
        color=SUCCESS_COLOR,
    )

    if game.cover_url:
        embed.set_thumbnail(url=game.cover_url)

    embed.add_field(name="📅 Ano", value=str(game.release_year) if game.release_year else "N/A", inline=True)
    embed.add_field(name="🏷️ Gêneros", value=genres_text, inline=True)
    embed.add_field(name="🖥️ Plataformas", value=platforms_text, inline=False)
    embed.set_footer(text="Use /rate para avaliar e /review para escrever uma review!")

    return embed
