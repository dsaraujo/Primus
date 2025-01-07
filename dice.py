
import random

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
        response = response + " (" + ('Success' if (modifier+roll)>ease else 'Failure') + ")"
  elif rolltype == 'spell':
      if ease != 0:
        if (modifier+roll) >= ease:
          response = response + " (Success with " + str((modifier+roll)-ease) + " plus penetration Score for Total Penetration)"
        else:
          response = response + " (Failure by " + str(ease-(modifier+roll)) + ")"
      else:
        response = response + " (" + ease_factor(modifier+roll) + ")"
  if reason != '':
      response = response + " for " + reason
  return response

def stress(username, modifier:int, botch:int, reason:str):  
  if modifier == 0:
          response = str(username) + " rolls a stress die"
  else:
      response = str(username) + " rolls a stress die plus " + str(modifier) 

  if botch == 0:
      response = response + " (no botch):\n"
  elif botch == 1:
      response = response + " (1 botch die):\n"
  else:
      response = response + " (" + str(botch) + " botch dice):\n"

  #Limit botch dice so someone doesn't crash the server with 999,999,999,999...
  if botch > 25:
      botch = 25
      response = response + "Botch dice capped at 25 to prevent server abuse.\n"

  multiplier = 1
  roll = random.randint(0, 9)
  
  if roll == 0:
      if botch == 0:
          # no botch dice, so it's just a zero
          response = response + "Result: " + str(modifier) + " (" + ease_factor(modifier+roll) + ")"
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
              response = response + "Result: 0 + " + str(modifier) + " = " + str(modifier) + " (" + ease_factor(modifier) + ", no botches!)"
          elif botches == 1:
              response = response + "Result: 0 (" + " (Failure, 1 botch!)"
          else:
              response = response + "Result: 0 " + " (Failure, " + str(botches) + " botches!)"
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
      
      if modifier == 0:
          response = response + "Result: " + str(roll * multiplier) + " (" + ease_factor(roll*multiplier) + ")"
      else:
          response = response + "Result: " + str(roll * multiplier) +  " + " + str(modifier) + " = " + str((roll*multiplier + modifier)) + " (" + ease_factor(roll*multiplier + modifier) + ")"

  if reason != '':
        response = response + " for " + reason
  
  return response