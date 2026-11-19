# AvroraVPN AI — 2D Cartoon MVP

Генерирует сценарий мультфильма через Gemini и собирает простую 2D-анимацию с двумя постоянными оригинальными персонажами (Бублик и Пиксель) через Pillow + FFmpeg.

## Подключение
GitHub → Settings → Secrets and variables → Actions → New repository secret:
- Name: `GEMINI_API_KEY`
- Value: API key из https://aistudio.google.com/apikey

## Проверка
Actions → AvroraVPN 2D Cartoon → Run workflow.
После завершения открой запуск и скачай MP4 из Artifacts.

## Важно
Это рабочий прототип: персонажи рисуются программно, двигаются и показывают реплики. Это не полноценная нейросетевая покадровая генерация сложной 2D-графики. Озвучка и публикация в TikTok пока не подключены. GitHub Actions имеет лимиты бесплатного тарифа; запуск каждый час и рендер 24/7 не гарантированы. Для TikTok нужна официальная авторизация и одобрение Content Posting API.
