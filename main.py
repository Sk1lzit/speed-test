import asyncio
import aiohttp
import time
import argparse
import sys

async def measure_download(session, url: str, num_requests: int = 10):
    total_bytes = 0
    total_time = 0.0
    successful_requests = 0

    print(f"\n[*] Начинаю замер для: {url}")
    print(f"[*] Количество запросов: {num_requests}\n")

    for i in range(1, num_requests + 1):
        try:
            start_time = time.perf_counter()
            
            # ВАЖНО: User-Agent для обхода блокировок (403)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                response.raise_for_status() 
                data = await response.read()
                
            end_time = time.perf_counter()
            
            elapsed = end_time - start_time
            bytes_downloaded = len(data)
            
            total_time += elapsed
            total_bytes += bytes_downloaded
            successful_requests += 1
            
            print(f"  [{i}/{num_requests}] Скачано: {bytes_downloaded / 1024:.2f} КБ за {elapsed:.3f} сек.")

        except aiohttp.ClientResponseError as e:
            print(f"  [!] Ошибка на запросе {i}: Сервер вернул статус {e.status} ({e.message})")
        except Exception as e:
            print(f"  [!] Ошибка на запросе {i}: {e}")

    # Финальный расчет
    if total_time > 0 and total_bytes > 0:
        avg_time = total_time / successful_requests
        
        speed_bps = total_bytes / total_time
        speed_kbps = (speed_bps / 1024)
        speed_mbps = (speed_bps * 8) / (1024 * 1024) 

        print("\n" + "="*40)
        print("РЕЗУЛЬТАТЫ ИЗМЕРЕНИЯ:")
        print(f"Успешных запросов: {successful_requests} из {num_requests}")
        print(f"Общий скачанный объем: {total_bytes / 1024:.2f} КБ")
        print(f"Среднее время на 1 запрос: {avg_time:.3f} сек")
        print(f"Средняя скорость: {speed_kbps:.2f} КБ/с ({speed_mbps:.2f} Мбит/с)")
        print("="*40)
    else:
        print("\n[!] Не удалось собрать статистику. Все запросы провалились.")

async def main():
    # Настройка парсера аргументов командной строки
    parser = argparse.ArgumentParser(description="Скрипт для замера скорости скачивания файлов.")
    parser.add_argument("url", type=str, help="Ссылка на файл (например, картинку)")
    parser.add_argument("-n", "--num", type=int, default=10, help="Количество запросов (по умолчанию 10)")
    
    args = parser.parse_args()

    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        await measure_download(session, args.url, num_requests=args.num)

if __name__ == "__main__":
    # Проверка, что скрипт запускают напрямую, а не импортируют
    if len(sys.argv) < 2:
        print("Использование: python main.py <URL> [-n КОЛИЧЕСТВО]")
        print("Пример: python main.py https://example.com/image.jpg -n 5")
        sys.exit(1)
        
    asyncio.run(main())