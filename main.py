'''
Resumo de videos do youtube

passo para o projeto
1. Receber o link do video
2. Acessar a transcrição do video no youtube
3. Extrair o texto da transcrição
4. Enviar o texto para a API do resumo
5. Receber o resumo da API
6. Exibir o resumo para o usuário

Tecnologias;
- Streamlit
- Youtube Data API
- OpenAI API
'''
import streamlit as st
import openai
import requests
import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
import os
from dotenv import load_dotenv


# Carregar as variáveis do arquivo .env
load_dotenv()

# Configurações da API

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def extract_video_id(video_url):
    import re
    # Padrões para diferentes formatos de URL do YouTube
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)",  # URL padrão
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]+)",  # Vídeos ao vivo
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)"  # URLs curtas
    ]

    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)

    return None


def get_video_transcription(video_id):
    try:
        # Obtém a transcrição em português, se disponível
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt'])
        # Concatena os textos
        transcription = ' '.join([item['text'] for item in transcript])
        return transcription
    except TranscriptsDisabled:
        return "Transcrição não está disponível para este vídeo."
    except Exception as e:
        return f"Erro ao obter transcrição: {e}"


# Função para resumir texto com OpenAI
def summarize_text(text):

    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        # Novo formato para a API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente que resume textos."},
                {"role": "user", "content": f"Resuma o seguinte texto:\n\n{text}"}
            ]
        )
        # Retorna o conteúdo do resumo
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro ao resumir texto: {e}"


# Aplicativo Streamlit
def main():
    st.title("Resumo de Vídeos do YouTube")

    video_url = st.text_input("Insira o link do vídeo do YouTube:")
    if st.button("Gerar Resumo"):
        try:
            # Extrair ID do vídeo
            video_id = extract_video_id(video_url)
            st.write(video_id)
            if not video_id:
                st.error("URL inválida. Insira um link de vídeo válido do YouTube.")
                return

            # Passo 3: Obter transcrição
            st.info("Obtendo a transcrição do vídeo...")
            transcription = get_video_transcription(video_id)
            if "Transcrição não encontrada" in transcription:
                st.error(transcription)
                return

            # Passo 4: Enviar texto para a API do resumo
            st.info("Resumindo a transcrição...")

            # st.write(transcription)
            summary = summarize_text(transcription)

            # Passo 6: Exibir o resumo
            st.success("Resumo gerado com sucesso!")
            st.text_area("Resumo", summary, height=300)

            # Botão para download da transcrição
            st.download_button(
                label="Baixar Transcrição Completa",
                data=transcription,
                file_name="transcription.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Erro: {e}")


if __name__ == '__main__':
    main()

