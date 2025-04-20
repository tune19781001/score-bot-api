import os
import json
from upload_to_drive import upload_to_drive
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone as LangchainPinecone
from langchain.memory import VectorStoreRetrieverMemory
from langchain.chains.conversation.memory import ConversationBufferMemory
from pinecone import Pinecone

# ✅ APIキー読み込み
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "your-key")
INDEX_NAME = "judgment-log"

# ✅ Pinecone初期化
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
embedding = OpenAIEmbeddings()
vectorstore = LangchainPinecone(index=index, embedding=embedding, text_key="text")

# ✅ メモリ初期化
memory_retriever = VectorStoreRetrieverMemory(retriever=vectorstore.as_retriever())
conversation_memory = ConversationBufferMemory(return_messages=True)

# ✅ 保存ファイル名（JSON）
MEMORY_LOG_FILE = "conversation_history.json"

# ✅ 会話ログ保存関数（＋Google Driveへアップロード）
def save_conversation_to_file():
    messages = conversation_memory.chat_memory.messages
    data = [{"role": msg.type, "text": msg.content} for msg in messages]
    with open(MEMORY_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ 会話履歴をファイルに保存しました")

    # ✅ Google Drive にアップロード
    upload_to_drive()

# ✅ 判断ログ保存
def save_judgment(input_text: str, result: str):
    memory_retriever.save_context({"input": input_text}, {"output": result})
    print("Saved judgment to Pinecone.")

# ✅ 類似判断の検索
def search_similar(input_text: str):
    return memory_retriever.load_memory_variables({"input": input_text})

# ✅ 会話記録（＋保存＋Driveアップロード）
def update_conversation(user_input: str, bot_output: str):
    conversation_memory.save_context({"input": user_input}, {"output": bot_output})
    save_conversation_to_file()

# ✅ 会話履歴取得（直近n件）
def get_conversation_history(limit=3):
    messages = conversation_memory.chat_memory.messages[-limit*2:]
    history = ""
    for i in range(0, len(messages), 2):
        user = messages[i].content
        bot = messages[i+1].content if i+1 < len(messages) else ""
        history += f"input: {user}\noutput: {bot}\n"
    return history

# ✅ 応答生成（＋保存）
def get_response(user_input: str):
    conversation_memory.chat_memory.add_user_message(user_input)
    response = f"You said: {user_input}"
    conversation_memory.chat_memory.add_ai_message(response)
    save_conversation_to_file()
    return response
