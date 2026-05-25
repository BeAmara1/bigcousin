import discord


class PaginatorView(discord.ui.View):
    def __init__(self, items, items_per_page, render_page, timeout=180):
        super().__init__(timeout=timeout)
        self.items = items
        self.items_per_page = items_per_page
        self.render_page = render_page
        self.current_page = 0
        self.max_page = max(0, (len(items) - 1) // items_per_page)
        self._update_buttons()

    def _update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.max_page

    def _get_page_items(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self._update_buttons()
        await self._update(interaction)

    @discord.ui.button(label="⏹", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        try:
            await interaction.message.delete()
        except discord.HTTPException:
            pass

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self._update_buttons()
        await self._update(interaction)

    async def _update(self, interaction: discord.Interaction):
        page_items = self._get_page_items()
        embed = await self.render_page(page_items, self.current_page, self.max_page + 1)
        await interaction.response.edit_message(embed=embed, view=self)

    async def start(self, interaction: discord.Interaction):
        page_items = self._get_page_items()
        embed = await self.render_page(page_items, self.current_page, self.max_page + 1)
        await interaction.response.send_message(embed=embed, view=self)
