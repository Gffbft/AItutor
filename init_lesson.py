import engine
import random
# access database

data = {
        "language1": "",
        "language2": "",
        "currentLevel": "A1",
        "desiredLevel": "A2",
        "lessonCount": 0,
        "SmallTalkTopics": [],
        "mistakes": [],
        "LearningPlan": [],
        }

language1 = data["language1"]
language2 = data["language2"]
currentLevel = data["currentLevel"]
desiredLevel = data["desiredLevel"]
lessonCount = data["lessonCount"]
mistake = random.choice(data["mistakes"])
SmallTalkTopic = random.choice(data["SmallTalkTopics"])
mistakes = random.choice(data["mistakes"])
if not mistakes:
        mistake = random.choice(mistakes)
        data["mistakes"].remove(mistake)
else:
        mistake = ""

learningPlan = data["LearningPlan"][lessonCount]

conv = engine.ChatEngine(language1, language2, currentLevel, desiredLevel, lessonCount, SmallTalkTopic, mistake,
                         learningPlan)

lessonCount += conv.conversation()

mistakes.append(conv.check_mistakes())
