# bot-line
NuxtImageBoard apiを用いる簡易LineBot

## Features
[l-m-api3](https://github.com/Dosugamea/l-m-api3)を使用(簡単にかける)  
flexメッセージいっぱい(見た目がよい)  
Docker対応

## Installation
### 1 引っ張ってくる
```Dockerfile
docker pull dosugamea/bot-line:amd64  
OR  
docker pull dosugamea/bot-line:armv7
```
### 2 環境変数(.env)を書く
```text
LINE_CHANNEL_TOKEN=HOGE
CDN_ENDPOINT=https://nboard-api.domao.site/static/
API_ENDPOINT=https://nboard-api.domao.site
API_TOKEN=NB_TOKEN
```
### 3 動かす
```Dockerfile
docker run --rm --env-file=<envファイルパス> -p <受付ポート>:1204 -t nuxt-image-board/bot-line
```

## Build
```text
docker build -f Dockerfile_amd64 -t nuxt-image-board/bot-line-pc .
```
```text
docker buildx build --platform linux/arm/v7 --file Dockerfile_armv7 --t nuxt-image-board/bot-line .
```