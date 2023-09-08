import openai
import time
import numpy as np
import random
import os

openai.api_key = os.environ.get("OPEN_AI_TOKEN")

PATHS = {"SYSTEM_PROMPT": r".\Prompts\NewSystemPrompt.txt",
         "MISTAKES_CHECKING_PROMPT": r".\Prompts\Mistakes Checking Prompt.txt",
         "GENERAL_SUMMARIZING_PROMPT": r".\Prompts\General summarizing prompt.txt",
         "SMALL_TALK_TOPICS": r".\Prompts\SmallTalk Topics.txt",
         "LEARNING_PLAN_PROMPT": r".\Prompts\Learning Plan.txt"}


def save_array(data, saveDir):
    file = np.load(saveDir)
    np.append(file, data)
    np.save(saveDir, data)


class ChatEngine:

    def __init__(self, language1, language2, currentLevel, desiredLevel, lessonCount=0, smallTalkTopics="Weather", mistake="", plan=""):
        with open(PATHS["SYSTEM_PROMPT"]) as file:
            self.instructions = file.read()
        file.close()

        with open(PATHS["MISTAKES_CHECKING_PROMPT"]) as file:
            self.UniversalMistakesCheckingPrompt = file.read()
        file.close()

        with open(PATHS["SMALL_TALK_TOPICS"]) as file:
            self.SmallTalkTopicsPrompt = file.read()
        file.close()

        with open(PATHS["LEARNING_PLAN_PROMPT"]) as file:
            LearningPlan = file.read().replace("\n", "")
        file.close()

        self.currentLevel = currentLevel
        self.desiredLevel = desiredLevel
        self.language1 = language1
        self.language2 = language2
        self.plan = plan
        self.lessonCount = lessonCount
        self.smallTalkTopics = smallTalkTopics
        self.mistake = mistake
        self.chatLog = []
        self.topics = []
        self.listOfAnswers = []
        self.arrayOfTopics = []
        self.topicsToTarget = []
        self.LearningPlan = LearningPlan.format(language1=language1, language2=language2, level=currentLevel,
                                                desiredLevel=desiredLevel)
        self.instruction_generation()
        self.prompt = {"role": "system", "content": self.instruction_generation()}
        self.messages = [self.prompt]

    def conversation(self, messages):

        self.listOfAnswers.append(messages[-1]["content"])
        self.chatLog.append(f"Student:{messages[-1]}")
        self.messages.append({"role": "assistant", "content": messages[-1]})
        print(messages[-6:])
        print([self.prompt] + messages[-6:])
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[self.prompt] + messages[-6:],
            max_tokens=1000,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
            n=1,
        )
        chat_response = completion.choices[0].message["content"]
        self.chatLog.append(f"Tutor:{chat_response}")

        print(f'ChatGPT: {chat_response}')

        self.messages.append({"role": "assistant", "content": chat_response})

        if self.list_items_separator(chat_response) == 4 or 'STOP' in chat_response:
            print('THE_LESSON_IS_OVER_HOORAY')
            return 1, chat_response
        else:
            return 0, chat_response

    def check_mistakes(self, content):
        mistakes_checking_prompt = self.UniversalMistakesCheckingPrompt.format(message=content,
                                                                               language1=self.language1,
                                                                               language2=self.language2,
                                                                               native_language=self.language1)
        mistakes_checker = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": mistakes_checking_prompt}]
        )
        return mistakes_checker.choices[0].message.content

    def mistakes_to_topics(self):

        listOfAnswers = self.listOfAnswers
        for response in listOfAnswers:
            topicsToTargetInTheResponse = self.check_mistakes(response)
            if "NO_MISTAKES" not in topicsToTargetInTheResponse:
                self.topicsToTarget.append(topicsToTargetInTheResponse.split(","))
            print(f'{response}Corrections: {self.check_mistakes(response)}')

            time.sleep(20)

        return self.topicsToTarget

    def summarize_chatlog(self, messages):

        response = openai.ChatCompletion.create(
            model='text-ada-001',
            prompt=f""" "{self.chatLog}"this is a chat log between a student and a teacher.
             Summarize the chat log briefly, focusing on key points and main topics discussed. The summary should be as 
             short as possible""",
            max_tokens=100,
            temperature=0.3,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
            n=1,
        )
        return (response.choices[0].text)

    def summary_prompt(self):
        last_messages = self.chatLog[-5:]
        last_messages = '\n '.join([str(elem) for elem in last_messages])
        previous_messages = '\n '.join([str(elem) for elem in self.chatLog[:-6]])

        with open(PATHS["GENERAL_SUMMARIZING_PROMPT"]) as file:
            GSP = file.read()
        if len(self.chatLog) > 6:
            summary = self.summarize_chatlog(previous_messages)
            GeneralSummarizingPrompt = GSP.format(instructions=self.instruction_generation(),
                                                  summary=summary,
                                                  conversation=last_messages)
        else:
            GSP = GSP.replace(
                r"is the summary of what you were talking about at the beginning if the lesson: {summary}, "
                "and here", "")

            GeneralSummarizingPrompt = GSP.format(instructions=self.instruction_generation(),
                                                  summary="",
                                                  conversation=last_messages,)

        return GeneralSummarizingPrompt

    def small_talk_topics(self):

        topics = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": self.SmallTalkTopicsPrompt}],
            max_tokens=100,
            temperature=0.3,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
            n=1,
        )

        topics = topics.choices[0].message.content.replace("\n", "").split(",")
        print(self.arrayOfTopics)
        topics.pop(0)
        return topics

    def learning_plan_generation(self):
        with open(PATHS["LEARNING_PLAN_PROMPT"]) as file:
            LearningPlan = file.read().replace("\n", "")
        file.close()
        LearningPlan = LearningPlan.format(language1=self.language1, language2=self.language2, level=self.currentLevel,
                                           desiredLevel=self.desiredLevel)
        plan = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content":LearningPlan}],
            max_tokens=1000,
            temperature=0.3,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
            n=1,
        )
        arrayOfPlans = plan.choices[0].message.content.replace("\n", "").split(";;;")
        return arrayOfPlans

    def instruction_generation(self):
        print(self.smallTalkTopics)
        smallTalkTopic = random.choice(self.smallTalkTopics)
        self.instructions = self.instructions.format(language1=self.language1, language2=self.language2,
                                                     small_talk_topic=smallTalkTopic, mistake=self.mistake,
                                                     plan=self.plan)
        return self.instructions

    def list_items_separator(self, message):
        if "[1]" in message:
            return 1
        if "[2]" in message:
            return 2
        if "[3]" in message:
            return 3
        if "[4]" in message:
            return 4
