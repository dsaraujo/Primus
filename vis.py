import re
import io
import random
import csv
from collections import Counter

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
    "creo": "✨", "intellego": "👁️", "muto": "🦋", "perdo": "🍂", "rego": "⚖️",
    "animal": "🐾", "aquam": "💧", "auram": "💨", "corpus": "👤", "herbam": "🌿",
    "imaginem": "🎭", "ignem": "🔥", "mentem": "🧠", "terram": "⛰️", "vim": "🌀"
}

async def setup_marbles(interaction: discord.Interaction, role: discord.Role, vis: str):
    """Starts the marble distribution setup process."""
    if marble_game["is_active"]:
        await interaction.response.send_message(
            "A vis distribution is already in progress! Please use `/distribute` to finish it first.",
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
        description=f"Click a button below to claim your preferred vis. The distribution will be finalized with `/distribute`.",
        color=discord.Color.blue()
    )
    marble_list_str = "\n".join(
        f"{COLOR_EMOJIS.get(c, '🔹')} **{c.capitalize()}**: {v} available" for c, v in inventory.items()
    )
    embed.add_field(name="Available Vis", value=marble_list_str, inline=False)
    # embed.add_field(name="Participants", value=f"{len(participants)} members from the '{role.name}' role.", inline=False)
    
    await interaction.response.send_message(embed=embed, view=view)
    # Store the message so we can potentially disable the buttons later
    marble_game["message"] = await interaction.original_response()

async def distribute_marbles(interaction: discord.Interaction):
    """Finalizes the distribution, allocating marbles to users."""
    if not marble_game["is_active"]:
        await interaction.response.send_message("No vis distribution is currently active. Use `/setup` to start one.", ephemeral=True)
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

    # --- 0. Check if enough marbles ---
    total_marbles = sum(inventory.values())
    if total_marbles < len(participants):
        embed = discord.Embed(
            title="🧙 Vis Distribution Results",
            description="Not enough vis to distribute to all participants. Each participant receives zero.",
            color=discord.Color.red()
        )
        for user_id in participants:
            member = interaction.guild.get_member(user_id)
            if member:
                embed.add_field(name=member.display_name, value="None", inline=False)
        marble_game.update({
            "is_active": False, "inventory": {}, "participants": set(),
            "preferences": {}, "message": None, "starter_id": None
        })
        await interaction.followup.send(embed=embed)
        return

    # --- 1. Distribute marbles fairly, honoring preferences ---
    marbles_left = sum(inventory.values())
    num_participants = len(participants)
    marbles_per_user = marbles_left // num_participants    

    # Shuffle for fairness
    random.shuffle(participants)

    # Build a flat list of all marbles
    marble_pool = []
    for color, count in inventory.items():
        marble_pool.extend([color] * count)
    random.shuffle(marble_pool)

    # Assign marbles per user, honoring preferences
    distribution = {user_id: [] for user_id in participants}
    assigned_indices = set()
    for round_num in range(marbles_per_user):
        for user_id in participants:
            preferred = preferences.get(user_id)
            # Try to assign preferred marble if available
            found = False
            if preferred:
                for i, marble in enumerate(marble_pool):
                    if i in assigned_indices:
                        continue
                    if marble == preferred:
                        distribution[user_id].append(marble)
                        assigned_indices.add(i)
                        found = True
                        break
            # If not found, assign any available marble
            if not found:
                for i, marble in enumerate(marble_pool):
                    if i not in assigned_indices:
                        distribution[user_id].append(marble)
                        assigned_indices.add(i)
                        break

    # Calculate leftovers
    leftovers = [marble_pool[i] for i in range(len(marble_pool)) if i not in assigned_indices]

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

    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer, delimiter='\t')
    csv_writer.writerow(["Amount", "Art", "Kind", "Notes"])
    for user_id, marbles in distribution.items():
        member = interaction.guild.get_member(user_id)
        if member and marbles:
            marble_counts = Counter(marbles)
            for color, amount in marble_counts.items():
                csv_writer.writerow([-amount, color.capitalize(), "Magic", "Divisão do Covenant - " + member.display_name])

    csv_buffer.seek(0)
    discord_file = discord.File(fp=io.BytesIO(csv_buffer.getvalue().encode()), filename="vis_distribution.csv")

    # --- 5. Clean Up ---
    # Disable buttons on the original message
    try:
        if marble_game["message"]:
            channel = interaction.guild.get_channel(marble_game["message"].channel.id)
            if channel:
                original_message = await channel.fetch_message(marble_game["message"].id)
                await original_message.edit(view=None)
    except (discord.NotFound, discord.Forbidden, AttributeError):
        print("Could not find or edit the original setup message.")
    
    # Reset the game state for the next run
    marble_game.update({
        "is_active": False, "inventory": {}, "participants": set(),
        "preferences": {}, "message": None, "starter_id": None
    })

    await interaction.followup.send(embed=embed, file=discord_file)
    
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

        # --- Update the setup message with current preferences ---
        if marble_game["message"]:
            # Build a list of users who have picked a preference
            guild = interaction.guild
            picked = []
            for user_id, color in marble_game["preferences"].items():
                member = guild.get_member(user_id)
                if member:
                    color_emoji = COLOR_EMOJIS.get(color.lower(), "🔹")
                    picked.append(f"{member.display_name}: {color_emoji} **{color.capitalize()}**")
            picked_str = "\n".join(picked) if picked else "No preferences yet."

            # Edit the embed
            original_message = await marble_game["message"].edit(
                embed=None, view=self
            )  # fetch the message object if needed
            embed = original_message.embeds[0] if original_message.embeds else discord.Embed(
                title="🎉 Vis Distribution Setup!",
                description=f"Click a button below to claim your preferred vis. The distribution will be finalized with `/distribute`.",
                color=discord.Color.blue()
            )
            # Remove any previous "Preferences" field

            embed.clear_fields()
            # Rebuild fields
            marble_list_str = "\n".join(
                f"{COLOR_EMOJIS.get(c, '🔹')} **{c.capitalize()}**: {v} available" for c, v in marble_game['inventory'].items()
        )
            embed.add_field(name="Available Vis", value=marble_list_str, inline=False)
            #embed.add_field(
            #    name="Participants",
            #    value=f"{len(marble_game['participants'])} members.",
            #    inline=False
            #)
            embed.add_field(name="Preferences", value=picked_str, inline=False)
            await marble_game["message"].edit(embed=embed, view=self)

