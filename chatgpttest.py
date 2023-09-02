#import os
import openai
import time
import numpy as np
from numpy import loadtxt
from numpy import asarray
openai.api_key = "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"

# Prompts

with open(r".\Prompts\System Prompt.txt") as f:
  mystuff = f.read()
f.close()

with open(r".\Prompts\Mistakes Checking Prompt.txt") as f:
  UniversalMistakesCheckingPrompt = f.read()
f.close()

mystuff = str(mystuff)
# data about languages
language1 = input("Type in a language you already speak:")
language2 = input("Type in a language you want to learn:")

# formatting
mystuff = mystuff.format(language1=language1, language2=language2, topics="learning serbian from scratch")

messages = [
 {"role": "system", "content": mystuff}
]
listOfAnswers = []
topicsToTarget = []


def check_mistakes(content):
  mistakesCheckingPrompt = UniversalMistakesCheckingPrompt.format(message=content, language1=language1,
                                                                  language2=language2, native_language=language1)
  print(mistakesCheckingPrompt)
  mistakes_checker = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "assistant", "content": mistakesCheckingPrompt}]
  )
  return mistakes_checker.choices[0].message.content

print(check_mistakes("jedan, dva, tri, četiri, pet, šest, sedam, osam, devet, deset"))
while True:
  content = input("User: ")
  listOfAnswers.append(content)
  messages.append({"role": "assistant", "content": content})

  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
  )

  chat_response = completion.choices[0].message.content

  print(f'ChatGPT: {chat_response}')

  messages.append({"role": "system", "content": chat_response})
  if 'STOP' in chat_response:
    print('THE_LESSON_IS_OVER_HOORAY')
    break

for response in listOfAnswers:
  topicsToTargetInTheResponse = check_mistakes(response)
  if not "NO_MISTAKES" in topicsToTargetInTheResponse:
    topicsToTarget.append(topicsToTargetInTheResponse.split(","))
  print(f'{response}Corrections: {check_mistakes(response)}')
  time.sleep(20)

#byte_array = bytes(topicsToTarget)
#with open(r".\workspace\mistakes.txt", 'wb') as f:
#  f.write(byte_array)

data = np.load(r".\workspace\mistakes.csv.npy")
np.append(data, topicsToTarget)
np.save(r'.\workspace\mistakes.csv', data)
