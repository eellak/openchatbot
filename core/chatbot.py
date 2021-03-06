import logging

from chatterbot import ChatBot, comparisons, response_selection

from core.model.fastText.fastTextTrainer import ChatterBotFastTextTrainer
from core.model.wordSimilarity.wordSimilarityTrainer import ChatterBotWordSimilarityTrainer

logging.basicConfig(level=logging.INFO)
trainer = None


def initLevenshtein(httpClient):
    global trainer
    chatbot = ChatBot(
        "Charlie",
        read_only=True,
        database_uri='sqlite:///database.db',
        logic_adapters=[
            {
                "import_path": "core.adapters.logicAdapter.MyLogicAdapter"
            }
        ],
        statement_comparison_function=comparisons.levenshtein_distance,
        response_selection_method=response_selection.get_first_response,
    )
    wordSimilarityTrainer = ChatterBotWordSimilarityTrainer(chatbot)
    wordSimilarityTrainer.setHttpClient(httpClient)
    wordSimilarityTrainer.train()
    return chatbot


def initFastText(httpClient):
    global fastTextTrainer
    chatbot = ChatBot(
        "FastText",
        read_only=True,
        # storage_adapter='core.storageAdapter.CustomStorageAdapter',
        logic_adapters=[
            {
                "import_path": "core.adapters.fastTextLogicAdapter.FastTextLogicAdapter"
            }
        ]
    )
    fastTextTrainer = ChatterBotFastTextTrainer(chatbot)
    fastTextTrainer.setHttpClient(httpClient)
    fastTextTrainer.train()
    return chatbot


def generateResponse(chatbotLevenshtein, chatbotFastText, question, languageCode, threshold):
    s1 = chatbotLevenshtein.get_response(question)
    args = {'additional_response_selection_parameters': {'languageCode': languageCode}}
    s2 = chatbotFastText.get_response(question, **args)

    if s1.confidence <= s2.confidence:
        response = ("FastText similarity", s2.text, s2.confidence)
    else:
        response = ("Levenshtein similarity", s1.text, s1.confidence)

    if response[2] <= float(threshold):
        return []
    return [response[1]]
