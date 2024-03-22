# Video Utils

[Click here to see this page in English](https://github.com/VictorAp12/video-utils/blob/main/readme-en.md)

Realiza conversões, muda atributo título do arquivo, combina legenda com arquivo de vídeo e extrai todas as faixas de legendas de um arquivo de video.

## Neste projeto existem 2 aplicativos:
1) Converte vídeos e audios para diferentes formatos;
2) Outro que combina video (mkv) e legenda (srt) em um só arquivo, além de mudar o atributo título de um vídeo ou audio e por fim, extrai legenda de vídeos.

<h3 align="center">App Conversor de Vídeos</h3>

<div align="center">
<img src="https://github.com/VictorAp12/video-utils/assets/148372228/f3d1d022-00a2-4ff6-a546-41aeff00c367" />
</div>

Sabe quando você precisa converter varios vídeos para outro formato e só consegue achar sites que fazem isso de maneira muito lenta ou limitada?
Este programa resolverá seus problemas, pois faz isso para audios e vídeos da maneira mais rápida e sem limite de quantidade.

<h3 align="center">App Mudar Atributos de Vídeos</h3>

<div align="center">
<img src="https://github.com/VictorAp12/video-utils/assets/148372228/faaabc82-d3d2-42a1-a3c3-b70b7200d5e9" />
</div>

Sabe quando você vai assistir um vídeo em algum dispositivo e o título e totalmente aleatório e mesmo mudando o nome do arquivo o nome do vídeo continua o mesmo?
Este programa resolve seus problemas, basta apertar o botão "mudar título" e pronto o título do video / audio será o mesmo do nome do arquivo, muito útil para quando está usando streaming de media a partir de um computador.

Já o botão "Juntar vídeo e legenda" combina dois arquivos em um só (video em mkv e legenda em srt), muito útil para quando o dispositivo usado não ter opção para procurar legenda mas disponibiliza ativá-la mudando entre as faixas de legenda.

Por fim o botão "Extrair Legenda de Vídeo" extrai todas as faixas de legendas do vídeo. Por padrão, as legendas são em formato srt, mas também é possível escolher outros como .ass.


Conteúdo:
- [Requisitos](#requisitos)
- [Instalação](#instalação)


## Requisitos
- Python 3.8 ou acima
- ffmpeg v3.1 ou acima. Link: http://ffmpeg.org/ instalado no seu $PATH

## Instalação

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
    python -m main
    ```
