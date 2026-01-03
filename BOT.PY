import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- ALTERA AQUI (NOMES DOS CARGOS DA STAFF) ----------
STAFF_ROLES = ["👑 00", "01", "👑 02", "03", "🔧 Gerente de farm"]

# ---------- ID DA CATEGORIA ONDE OS TICKETS DEVEM SER CRIADOS ----------
TICKET_CATEGORY_ID = 1455220016344727704 # <- substitui pelo ID da categoria no Discord

# guarda formularios por ticket
forms = {}   # {ticket_id: [ {user_id, user_name, resposta} ]}

# ---------- MODAL DO FORMULÁRIO ----------
class FormularioModal(Modal, title="Formulário de Produtos"):
    produto1 = TextInput(label="Produto 1 e Quantidade", placeholder="Ex: Farinha - 15kg", required=True)
    produto2 = TextInput(label="Produto 2 e Quantidade", placeholder="Ex: Açúcar - 15kg", required=True)
    produto3 = TextInput(label="Produto 3 e Quantidade", placeholder="Ex: Água - 5 litros", required=True)
    print_input = TextInput(label="Print/Prova", placeholder="Coloca aqui o link do print ou descrição", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        ticket_id = interaction.channel.id
        if ticket_id not in forms:
            forms[ticket_id] = []

        forms[ticket_id].append({
            "user_id": interaction.user.id,
            "user_name": interaction.user.name,
            "produto1": self.produto1.value,
            "produto2": self.produto2.value,
            "produto3": self.produto3.value,
            "print": self.print_input.value
        })

        await interaction.response.send_message("✅ Formulário enviado com sucesso!", ephemeral=True)

# ---------- BOTÕES PRINCIPAIS ----------
class TicketButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Criar Ticket", style=discord.ButtonStyle.green, custom_id="criar_ticket")
    async def criar_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)  # pega a categoria pelo ID

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # adicionar staff ao ticket
        for role in guild.roles:
            if role.name in STAFF_ROLES:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            category=category
        )

        await interaction.response.send_message(
            f"Ticket criado: {ticket.mention}", ephemeral=True
        )

        await ticket.send(
            f"{interaction.user.mention} abriu um ticket.",
            view=TicketActionsView(ticket.id)
        )

# ---------- BOTÕES DENTRO DO TICKET ----------
class TicketActionsView(View):
    def __init__(self, ticket_id):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(label="📝 Enviar Formulário", style=discord.ButtonStyle.blurple, custom_id="enviar_form")
    async def enviar_form(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(FormularioModal())

    @discord.ui.button(label="📂 Consultar Formulários", style=discord.ButtonStyle.gray, custom_id="consultar_form")
    async def consultar_form(self, interaction: discord.Interaction, button: Button):
        ticket_id = self.ticket_id

        if ticket_id not in forms or len(forms[ticket_id]) == 0:
            await interaction.response.send_message(
                "❌ Ainda não existem formulários neste ticket.",
                ephemeral=True
            )
            return

        texto = "📄 **Formulários deste ticket:**\n\n"
        for f in forms[ticket_id]:
            texto += f"👤 **{f['user_name']}**\n"
            texto += f"➡️ {f['produto1']}\n➡️ {f['produto2']}\n➡️ {f['produto3']}\n"
            if f['print']:
                texto += f"🖼️ Print: {f['print']}\n"
            texto += "\n"

        await interaction.response.send_message(texto, ephemeral=True)

# ---------- COMANDO PARA ENVIAR BOTÃO DE CRIAR TICKET ----------
@bot.command()
async def setup(ctx):
    view = TicketButtons()
    await ctx.send("Clique no botão abaixo para criar um ticket:", view=view)

# ---------- BOT READY ----------
@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")
    bot.add_view(TicketButtons())

# ---------- RODA O BOT ----------
bot.run("MTQ1NTYyNjEzMTYyMDIzMzQ3Mw.GuUwiN.xl5MKAdHkALppDs46OKzHt2Dj6WsK5OD7_x_oc")

