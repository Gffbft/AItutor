import engine
import openai
PATHS = engine.PATHS

language1 = input("What is your first language?")
language2 = input("What is your second language?")
currentLevel = input("What is your current level")
desiredLevel = input("What is your desired level")

initialize = engine.ChatEngine(language1, language2, currentLevel, desiredLevel, 0, "", "", "")
learningPlan = initialize.learning_plan_generation()
smallTalkTopics = initialize.small_talk_topics()
print(learningPlan)

# Save the data
