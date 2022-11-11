from os import path, getcwd, mkdir

EVENT_SEND_PHRASE_TO_ASSISTANT = "core-send-assistant-phrase"
EVENT_ON_ASSISTANT_RESPONSE = "core-assistant-response"
EVENT_ON_FOLLOWUP_START = "core-on-followup-start"
EVENT_ON_FOLLOWUP_MSG = "core-on-followup-msg"
EVENT_ON_FOLLOWUP_END = "core-on-followup-end"
EVENT_ON_SKILL_START = "core-on-skill-start"
EVENT_ON_SKILL_END = "core-on-skill-end"
EVENT_ON_PHRASE_PARSE_ERROR = "core-on-phrase-parse-error"


DIRECTORY_PLUGINS = path.normpath(path.join(getcwd(), 'plugins'))
DIRECTORY_DATA = path.normpath(path.join(getcwd(), 'data'))
DIRECTORY_DATA_CORE = path.normpath(path.join(getcwd(), 'data', 'core'))
DIRECTORY_DATA_CORE_INTENTS_INFERENCE = path.normpath(
    path.join(getcwd(), 'data', 'core','intents.ptf'))

SINGLETON_SERVER_ID = "singleton-server"
SINGLETON_ASSISTANT_ID = "singleton-assistant"
SINGLETON_MAIN_LOADER_ID = "singleton-main-loader"
SINGLETON_INTENTS_INFERENCE_ID = "singleton-intents-inference"

WAKE_WORD = 'alice'
if not path.exists(DIRECTORY_DATA_CORE):
    mkdir(DIRECTORY_DATA_CORE)
