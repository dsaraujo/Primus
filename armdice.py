
import random
import dice
import math

def ease_factor(total:int): 
    msg = ""
    if (total < 3):
        return "Trivial"
    elif (total < 6):
        return "Simple"
    elif (total < 9):
        return "Easy"
    elif (total < 12):
        return "Average"
    elif (total < 15):
        return "Hard"
    elif (total < 18):
        return "Very Hard"
    elif (total < 21):
        return "Impressive"
    elif (total < 24):
        return "Remarkable"
    else:
        return "Almost Impossible"

def roll(username, diceexpression:str, reason:str):
    try:
        roll = dice.roll(diceexpression)
        result = username + " rolled " + str(diceexpression) 
        if reason:
            result = result + " for " + reason 
        result = result + "\nResult: " + str(roll)
        return result
    except dice.DiceBaseException as e:
        print(e)
        return "Error: " + str(e)

def simple(username, modifier:int, rolltype:str, ease:int, reason:str):  
  roll = random.randint(1, 10)
  if modifier == 0:
      response = username + " rolls a simple die"
      if rolltype == 'skill' and ease > 0:
          response = response + " vs ease factor of " + str(ease)
      response = response + '\n'
      response = response + "Result: " + str(roll) 
  else:
      response = username + " rolls a simple die plus " + str(modifier)
      if rolltype == 'skill' and ease > 0:
          response = response + " vs ease factor of " + str(ease)
      response = response + '\n'
      response = response + "Result: " + str(roll) + " + " + str(modifier) + " = " + str(modifier+roll) 
  if rolltype == '':
      response = response + " (" + ease_factor(modifier+roll) + ")"
  elif rolltype == 'skill':
      if ease == 0:
        response = response + " (" + ease_factor(modifier+roll) + ")"
      else:
        response = response + " (" + ('Success' if (modifier+roll) >= ease else 'Failure') + ")"
  elif rolltype == 'spell':
      response = response + get_spell_result(roll, modifier, ease)
  if reason != '':
      response = response + " for " + reason
  return response

def get_spell_result(roll, modifier, ease):
    response = ''
    if ease != 0:
        if (modifier+roll) >= ease:
          response = response + " (Success, Total Penetration = " + str((modifier+roll)-ease) + " plus penetration score)"
        else:
          response = response + " (Failure by " + str(ease-(modifier+roll)) + ")"
    else:
        response = response + " (" + ease_factor(modifier+roll) + ")"
    return response

def get_max_base(total:int, magnitude:int):
    max_base = 0
    if total >= 5:
        # First, round total to the nearest 5
        total = math.floor(total / 5) * 5
        while total > 5 and magnitude > 0:
            total = total - 5            
            magnitude = magnitude - 1
        max_base = total
        while magnitude > 0:
            max_base = max_base - 1 
            magnitude = magnitude - 1
    else:
        max_base = total - magnitude
    return max_base

def cast(username, modifier:int, botch:int, magnitude:int, reason:str):
    
    if botch == 0:
        response = "You must have at least one botch dice for spontaneous spells"
        return response    

    response = str(username) + " cast an spontaneous spell, rolling a stress die plus " + str(modifier)
    
    if botch == 0:
        response = response + " (no botch)"
    elif botch == 1:
        response = response + " (1 botch die)"
    else:
        response = response + " (" + str(botch) + " botch dice)"
    response = response + ':\n'
    
    if botch > 25:
        botch = 25
        response = response + "Botch dice capped at 25 to prevent server abuse.\n"
    
    multiplier = 1
    roll = random.randint(0, 9)
  
    if roll == 0:
        response = response + "Rolled a 0, Checking for Botch: "
        botches = 0
        for b in range (1,botch+1):
            botchdie = random.randint(0,9)
            response = response + str(botchdie)
            if b < botch:
                response = response + ", "
            if botchdie == 0:
                botches = botches + 1
        response = response + "\n"
        if botches == 0:
            total = math.ceil(modifier/2)
            response = response + "Result: 0 + " + str(modifier) + " / 2 = " + str(total) + " (no botches!)"
        elif botches == 1:
            total = 0
            response = response + "Result: 0 (**Failure, 1 botch**!)"
        else:
            total = 0
            response = response + "Result: 0 (**Failure, " + str(botches) + " botches**!)"
        response = response + "\n"
    else:
        # a 0 was not rolled, so process the stress roll normally
        while roll == 1:
            if multiplier == 1:
                response = response + "Roll: "
            multiplier = multiplier * 2
            response = response + '1, '
            roll = random.randint(1,10)
        
        if multiplier > 1:
            response = response + str(roll)
            response = response + " (x" + str(multiplier) + ") = " + str(roll*multiplier) + "\n"
        
        total = math.ceil(((roll*multiplier) + modifier) / 2)

        response = response + "Result: (" + str(roll * multiplier) +  " + " + str(modifier) + ") / 2 = " + str(total) + "\n"

    if total > 0:
        max_base = get_max_base(total, magnitude)
        if max_base <= 0:
            response = response + "You cannot cast a spell with the given magnitude of +" + str(magnitude) + ".\n"
        else:
            response = response + "Given the magnitude of +" + str(magnitude) + " you can cast a spell up to the base of " + str(get_max_base(total, magnitude)) + "\n"

    if reason != '':
            response = response + " for " + reason

    return response

def stress_die_no_botch() -> int:
    """
    Rolls a stress die that cannot botch, as required for aging.
    - 1s double the next roll.
    - 0s on the die (represented by 10 here) are a result of 0.
    """
    roll = random.randint(1, 10)
    if roll == 1:
        multiplier = 2
        while True:
            reroll = random.randint(1, 10)
            if reroll == 1:
                # Cap multiplier to prevent theoretical infinite loops
                if multiplier >= 1024:
                    return 10 * multiplier 
                multiplier *= 2
            else:
                # On a re-roll, a '0' on the die counts as 10
                value = 10 if reroll == 10 else reroll
                return value * multiplier
    elif roll == 10:  # Represents a '0' on the die
        return 0
    else:
        return roll

def aging(username, age:int, modifier:int) -> str:
    """
    Performs an Ars Magica 5th Edition aging roll and returns a formatted string.

    Args:
        age: The character's age in years.
        modifier: The character's total aging roll modifier (from Longevity Ritual,
                  Living Conditions, etc.).
    
    Returns:
        A string describing the roll and its outcome.
    """
    if age < 35:
        return f"At age {age}, no aging roll is required."

    # Perform the no-botch stress die roll.
    # Replace stress_die_no_botch() with your own bot's function if you have one.
    d10_result = stress_die_no_botch()

    # Calculate the components of the aging roll.
    age_bonus = math.ceil(age / 10)
    aging_total = d10_result + age_bonus - modifier

    # Start building the output string for Discord.
    output_lines = []
    output_lines.append(f"**Aging Roll for Age {age}** (Modifier: `{modifier}`)")
    output_lines.append(f"`Stress Die: {d10_result} + Age Bonus: {age_bonus} - Modifier: {modifier} =` **Total: {aging_total}**")
    output_lines.append("---") # Creates a horizontal line in Discord

    # Determine the outcomes based on the Aging Rolls table (ArM5, p. 170).
    result_descriptions = []
    
    # First, determine the effect on apparent age.
    if aging_total <= 2:
        result_descriptions.append("No apparent aging.")
    else:
        result_descriptions.append("Apparent age increases by one year.")

    # Next, determine if any aging points are gained.
    if 10 <= aging_total <= 12:
        result_descriptions.append("Gain 1 Aging Point in **any** Characteristic.")
    elif aging_total == 13:
        result_descriptions.append("Gain sufficient Aging Points (in any Characteristics) to reach the next level in Decrepitude, and **must make a Crisis roll**.")
    elif aging_total == 14:
        result_descriptions.append("Gain 1 Aging Point in **Quickness**.")
    elif aging_total == 15:
        result_descriptions.append("Gain 1 Aging Point in **Stamina**.")
    elif aging_total == 16:
        result_descriptions.append("Gain 1 Aging Point in **Perception**.")
    elif aging_total == 17:
        result_descriptions.append("Gain 1 Aging Point in **Presence**.")
    elif aging_total == 18:
        result_descriptions.append("Gain 1 Aging Point in **Strength** and **Stamina**.")
    elif aging_total == 19:
        result_descriptions.append("Gain 1 Aging Point in **Dexterity** and **Quickness**.")
    elif aging_total == 20:
        result_descriptions.append("Gain 1 Aging Point in **Communication** and **Presence**.")
    elif aging_total == 21:
        result_descriptions.append("Gain 1 Aging Point in **Intelligence** and **Perception**.")
    elif aging_total >= 22:
        result_descriptions.append("Gain sufficient Aging Points (in any Characteristics) to reach the next level in Decrepitude, and **must make a Crisis roll**.")

    # If there were no specific aging point results, add a "no effect" line.
    if not result_descriptions:
         result_descriptions.append("No further effects.")
         
    # Join all the description parts into the final output
    output_lines.extend(result_descriptions)

    return "\n".join(output_lines)

def stress(username, modifier:int, botch:int, rolltype:str, ease:int, reason:str):  
  if modifier == 0:
          response = str(username) + " rolls a stress die"
  else:
      response = str(username) + " rolls a stress die plus " + str(modifier)   

  if botch == 0:
      response = response + " (no botch)"
  elif botch == 1:
      response = response + " (1 botch die)"
  else:
      response = response + " (" + str(botch) + " botch dice)"
        
  if rolltype == 'skill' and ease > 0:
          response = response + " vs ease factor of " + str(ease)
  elif rolltype == 'spell' and ease > 0:
          response = response + " vs spell target of " + str(ease)
  response = response + ':\n'

  #Limit botch dice so someone doesn't crash the server with 999,999,999,999...
  if botch > 25:
      botch = 25
      response = response + "Botch dice capped at 25 to prevent server abuse.\n"

  multiplier = 1
  roll = random.randint(0, 9)
  
  if roll == 0:
      if botch == 0:
          # no botch dice, so it's just a zero
          if rolltype == '':
            response = response + "Result: " + str(modifier) + " (" + ease_factor(modifier) + ")"
          elif rolltype == 'skill' and ease > 0:
            response = response + "Result: " + str(modifier) + " (" + ('Success' if modifier >= ease else 'Failure') + ")"
          elif rolltype == 'spell' and ease > 0:
            response = response + get_spell_result(roll, modifier, ease)
              
      elif botch > 0:
          response = response + "Rolled a 0, Checking for Botch: "
          botches = 0
          for b in range (1,botch+1):
              botchdie = random.randint(0,9)
              response = response + str(botchdie)
              if b < botch:
                  response = response + ", "
              if botchdie == 0:
                  botches = botches + 1
          response = response + "\n"
          if botches == 0:
              if rolltype == '':
                response = response + "Result: 0 + " + str(modifier) + " = " + str(modifier) + " (" + ease_factor(modifier) + ", no botches!)"
              elif rolltype == 'skill' and ease > 0:
                response = response + "Result: 0 + " + str(modifier) + " = " + str(modifier) + " (" + ('Success' if modifier >= ease else 'Failure') + ", no botches!)"
              elif rolltype == 'spell' and ease > 0:
                response = response + "Result: 0 + " + str(modifier) + " = " + str(modifier) + get_spell_result(roll, modifier, ease) + " (no botches!)"
          elif botches == 1:
              response = response + "Result: 0 (**Failure, 1 botch**!)"
          else:
              response = response + "Result: 0 (**Failure, " + str(botches) + " botches**!)"
  else:
      # a 0 was not rolled, so process the stress roll normally
      while roll == 1:
          if multiplier == 1:
              response = response + "Roll: "
          multiplier = multiplier * 2
          response = response + '1, '
          roll = random.randint(1,10)
      
      if multiplier > 1:
          response = response + str(roll)
          response = response + " (x" + str(multiplier) + ") = " + str(roll*multiplier) + "\n"
      
      if rolltype == '':
        if modifier == 0:
            response = response + "Result: " + str(roll * multiplier) + " (" + ease_factor(roll*multiplier) + ")"
        else:
            response = response + "Result: " + str(roll * multiplier) +  " + " + str(modifier) + " = " + str((roll*multiplier) + modifier) + " (" + ease_factor((roll*multiplier) + modifier) + ")"
      elif rolltype == 'skill' and ease > 0:
          response = response + "Result: " + str(roll * multiplier) +  " + " + str(modifier) + " = " + str((roll*multiplier) + modifier) + " (" + ('Success' if ((roll*multiplier) + modifier) >= ease else 'Failure') + ")"
      elif rolltype == 'spell' and ease > 0:
          response = response + "Result: " + str(roll * multiplier) +  " + " + str(modifier) + " = " + str((roll*multiplier) + modifier) + " " + get_spell_result(roll*multiplier, modifier, ease)

  if reason != '':
        response = response + " for " + reason
  
  return response
