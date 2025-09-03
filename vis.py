import re
from collections import Counter
import random

import discord
from discord.ext import commands

marble_game = {
  "is_active": False,
  "inventory": {},
  "participants": set(),
  "preferences": {}, # {user_id: color}
  "message": None,
  "starter_id": None
}

COLOR_EMOJIS = {
    "creo": "⚪", "intellego": "🟡", "muto": "🏳️‍🌈", "perdo": "⚫", "rego": "🟣",
    "animal": "🟤", "aquam": "🫧", "auram": "🟣", "corpus": "🔴", "herbam": "🟢",
    "imaginem": "🔵", "ignem": "🔥", "mentem": "🟠", "terram": "🟤", "vim": "✨"
}

# Creo is white, Intellego gold, Muto constantly fluctuating, Perdo black, Rego purple
# Animal brown, Aquam blue, Auram violet, Corpus dark red, Herbam green, 
# Imaginem pearly blue, Ignem bright red, Mentem orange, Terram dark brown, and Vim silver. 


async def setup_marbles(interaction: discord.Interaction, role: discord.Role, vis: str):
    """Starts the marble distribution setup process."""
    if marble_game["is_active"]:
        await interaction.response.send_message(
            "A vis distribution is already in progress! Please use `/distribute_vis` to finish it first.",
            ephemeral=True
        )
        return
        
    # --- 1. Parse the marble input string ---
    inventory = {}
    # Regex to find pairs of (number, color)
    parsed_marbles = re.findall(r'(\d+)\s+([a-zA-Z]+)', vis.lower())
    if not parsed_marbles:
        await interaction.response.send_message(
            "Invalid format! Please use a format like `10 creo, 5 terram, 8 vim`.",
            ephemeral=True
        )
        return
    
    for count, color in parsed_marbles:
        inventory[color] = int(count)
    
    # --- 2. Get participants from the specified role ---
    participants = {member.id for member in role.members if not member.bot}
    if not participants:
        await interaction.response.send_message(
            f"The role '{role.name}' has no members to distribute marbles to!",
            ephemeral=True
        )
        return

    # --- 3. Update the global game state ---
    marble_game.update({
        "is_active": True,
        "inventory": inventory,
        "participants": participants,
        "preferences": {},
        "starter_id": interaction.user.id
    })

    # --- 4. Send the message with preference buttons ---
    colors = list(inventory.keys())
    view = PreferenceView(colors)
    
    embed = discord.Embed(
        title="🎉 Vis Distribution Setup!",
        description=f"Click a button below to claim your preferred vis. The distribution will be finalized with `/distribute_vis`.",
        color=discord.Color.blue()
    )
    marble_list_str = "\n".join(
        f"{COLOR_EMOJIS.get(c, '🔹')} **{c.capitalize()}**: {v} available" for c, v in inventory.items()
    )
    embed.add_field(name="Available Vis", value=marble_list_str, inline=False)
    embed.add_field(name="Participants", value=f"{len(participants)} members from the '{role.name}' role.", inline=False)
    
    await interaction.response.send_message(embed=embed, view=view)
    # Store the message so we can potentially disable the buttons later
    marble_game["message"] = await interaction.original_response()

async def distribute_marbles(interaction: discord.Interaction):
    """Finalizes the distribution, allocating marbles to users."""
    if not marble_game["is_active"]:
        await interaction.response.send_message("No vis distribution is currently active. Use `/setup_vis` to start one.", ephemeral=True)
        return
    
    # Optional: Only allow the user who started the game to distribute
    if interaction.user.id != marble_game["starter_id"]:
        await interaction.response.send_message("Only the person who set up the game can distribute the marbles.", ephemeral=True)
        return
        
    await interaction.response.defer() # Acknowledge the command while we do the logic

    inventory = marble_game["inventory"].copy()
    participants = list(marble_game["participants"])
    preferences = marble_game["preferences"]
    distribution = {user_id: [] for user_id in participants}

    # --- 1. Prioritize Preferences ---
    # Shuffle users with preferences to randomly decide who gets a preferred marble if supply is limited
    preferred_users = list(preferences.keys())
    random.shuffle(preferred_users)
    
    for user_id in preferred_users:
        color = preferences[user_id]
        if inventory.get(color, 0) > 0:
            distribution[user_id].append(color)
            inventory[color] -= 1

    # --- 2. Randomly Distribute the Rest ---
    # Create a flat list of all remaining marbles
    remaining_pool = []
    for color, count in inventory.items():
        remaining_pool.extend([color] * count)
    random.shuffle(remaining_pool)
    
    # Shuffle participants to ensure random distribution order
    random.shuffle(participants)
    
    # Distribute remaining marbles one by one, cycling through users
    num_participants = len(participants)
    for i, marble in enumerate(remaining_pool):
        if i >= num_participants * (len(remaining_pool) // num_participants):
            break # Stop when we can't give one to everyone anymore
        recipient_id = participants[i % num_participants]
        distribution[recipient_id].append(marble)

    # --- 3. Calculate Remainder ---
    total_distributed = sum(len(marbles) for marbles in distribution.values())
    leftovers = remaining_pool[total_distributed:]

    # --- 4. Build and Send the Results Embed ---
    embed = discord.Embed(title="🧙 Vis Distribution Results", color=discord.Color.green())
    
    if not distribution:
         embed.description = "No marbles were distributed."
    else:
        for user_id, marbles in distribution.items():
            member = interaction.guild.get_member(user_id)
            if member:
                # Use Counter for a clean summary (e.g., 2x Red, 1x Blue)
                marble_counts = Counter(marbles)
                marble_str = ", ".join(
                    f"{COLOR_EMOJIS.get(c, '🔹')} **{marble_counts[c]}x {c.capitalize()}**" for c in sorted(marble_counts)
                ) if marbles else "None"
                embed.add_field(name=member.display_name, value=marble_str, inline=False)

    if leftovers:
        leftover_counts = Counter(leftovers)
        leftover_str = ", ".join(
            f"{COLOR_EMOJIS.get(c, '🔹')} **{leftover_counts[c]}x {c.capitalize()}**" for c in sorted(leftover_counts)
        )
        embed.add_field(name="Leftover Vis", value=leftover_str, inline=False)
    
    # --- 5. Clean Up ---
    # Disable buttons on the original message
    #try:
    #    if marble_game["message"]:
    #        # Fetch the original message and disable its view            
    #        original_message = await bot.get_channel(marble_game["message"].channel.id).fetch_message(marble_game["message"].id)
    #        await original_message.edit(view=None)
    #except (discord.NotFound, discord.Forbidden):
    #    print("Could not find or edit the original setup message.")
    
    # Reset the game state for the next run
    marble_game.update({
        "is_active": False, "inventory": {}, "participants": set(),
        "preferences": {}, "message": None, "starter_id": None
    })

    await interaction.followup.send(embed=embed)

    
class PreferenceView(discord.ui.View):
    def __init__(self, colors):
        # Set a long timeout, e.g., 6 hours. For a persistent view across bot restarts,
        # you would need to set timeout=None and handle it in an on_ready event.
        super().__init__(timeout=21600) 
        
        # Dynamically create a button for each color
        for color in colors:
            button = discord.ui.Button(
                label=color.capitalize(),
                style=discord.ButtonStyle.secondary,
                custom_id=color,
                emoji=COLOR_EMOJIS.get(color.lower())
            )
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        """Handles button clicks for color preference."""
        # Check if the user is part of the giveaway
        if interaction.user.id not in marble_game["participants"]:
            await interaction.response.send_message(
                "Sorry, you're not part of this marble distribution!",
                ephemeral=True
            )
            return

        # Get the color from the button's custom_id
        chosen_color = interaction.data["custom_id"]
        
        # Store the user's preference
        marble_game["preferences"][interaction.user.id] = chosen_color
        
        emoji = COLOR_EMOJIS.get(chosen_color.lower(), "")
        await interaction.response.send_message(
            f"Your preference has been set to {emoji} **{chosen_color.capitalize()}**!",
            ephemeral=True
        )

