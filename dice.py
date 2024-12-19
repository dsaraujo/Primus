
import random

def ease_factor(total:int): 
    msg = ""
    if (total <= 0):
        return "Trivial"
    elif (total <=3):
        return "Simple"
    elif (total <=6):
        return "Easy"
    elif (total <=9):
        return "Average"
    elif (total <=12):
        return "Hard"
    elif (total <=15):
        return "Very Hard"
    elif (total <=18):
        return "Impressive"
    elif (total <=18):
        return "Remarkable"
    else:
        return "Almost Impossible"

def simple(username, modifier:int):  
  roll = random.randint(1, 10)
  if modifier == 0:
      response = username + " rolls a simple die\n"
      response = response + "Result: " + str(roll) + " (" + ease_factor(roll) + ")"
  else:
      response = username + " rolls a simple die plus " + str(modifier) + "\n"
      response = response + "Result: " + str(roll) + " + " + str(modifier) + " = " + str(modifier+roll) + " (" + ease_factor(modifier+roll) + ")"
  return response

def stress(username, modifier:int, botch:int):  
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
              response = response + "Result: 0 + " + str(modifier) + " = " + str(modifier) + " (" + ease_factor(modifier+roll) + ", no botches!)"
          elif botches == 1:
              response = response + "Result: 0 (" + " (" + ease_factor(modifier+roll) + ", 1 botch!)"
          else:
              response = response + "Result: 0 " + " (" + ease_factor(modifier+roll) + ", " + str(botches) + " botches!)"
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
          response = response + "Result: " + str(roll * multiplier) + "(" + ease_factor(modifier+roll) + ")"
      else:
          response = response + "Result: " + str(roll * multiplier) +  " + " + str(modifier) + " = " + str((roll*multiplier + modifier)) + "(" + ease_factor(roll*multiplier + modifier) + ")"

  return response