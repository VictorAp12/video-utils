# Video Utils

[Click here to see this page in English](https://github.com/VictorAp12/video-utils/blob/main/readme-en.md)

Realiza conversões, combina legenda com arquivo de vídeo e muda atributo título do arquivo.

## Neste projeto existem 2 aplicativos:
1) Converte vídeos e audios para diferentes formatos;
2) Outro que combina video (mkv) e legenda (srt) em um só arquivo, além de mudar o atributo título de um vídeo ou audio.

### App Conversor de Vídeos

Sabe quando você precisa converter varios vídeos para outro formato e só consegue achar sites que fazem isso de maneira muito lenta ou limitada?
Este programa resolverá seus problemas, pois faz isso para audios e vídeos da maneira mais rápida e sem limite de quantidade.

### App Mudar Atributos de Vídeos

Sabe quando você vai assistir um vídeo em algum dispositivo e o título e totalmente aleatório e mesmo mudando o nome do arquivo o nome do vídeo continua o mesmo?
Este programa resolve seus problemas, basta apertar o botão mudar título e pronto o título do video / audio será o mesmo do nome do arquivo, muito útil para quando está usando streaming de media a partir de um computador.

Já o botão de juntar vídeo e legenda combina dois arquivos em um só (video em mkv e legenda em srt), muito útil para quando o dispositivo usado não ter opção para procurar legenda mas disponibiliza ativá-la mudando entre as faixas de legenda.


Conteúdo:
- [Requisitos](#requisitos)
- [Instalação](#instalacao)


## Requisitos
- Python 3.8 ou acima
- ffmpeg v3.1 ou acima. Link: http://ffmpeg.org/ instalado no seu $PATH

## Instalação

A maneira mais fácil é simplesmente baixando o video utils installer windows 64 bits.exe. [Clique aqui para ir ao arquivo de download](https://github.com/VictorAp12/video-utils/blob/main/video%20utils%20installer%20win%2064.exe)

Ou se preferir baixar o projeto inteiro:

  - Baixe o projeto como zip ou usando gitclone https://github.com/VictorAp12/video-utils.git

  - Crie o ambiente virtual na pasta do projeto:
    ```bash
    python -m venv venv
    ```

  - Ative o ambiente virtual na pasta do projeto:
    ```bash
    venv\Scripts\activate
    ```

  - Instale as dependencias do projeto:
    ```bash
    pip install -r requirements.txt
    ```

  - Execute o main.py:
    ```bash
    python -m main.py
    ```
