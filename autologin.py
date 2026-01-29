#!/usr/bin/env python3
"""
AutoLogin - Автоматический вход на образовательный портал
Версия для сборки в EXE
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path

# Проверяем и импортируем Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    print("❌ Ошибка: Selenium не установлен!")
    print("Установите: pip install selenium")

class AutoLoginApp:
    def __init__(self):
        self.version = "2.1"
        self.website = "https://poo.edu-74.ru/security/#/login"
        
        # Пути файлов
        if getattr(sys, 'frozen', False):
            self.app_dir = Path(sys.executable).parent
        else:
            self.app_dir = Path(__file__).parent
        
        self.config_path = self.app_dir / "autologin_config.json"
        self.log_path = self.app_dir / "autologin_log.txt"
    
    def log(self, message):
        """Логирование"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        
        print(log_msg)
        
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(log_msg + "\n")
        except:
            pass
    
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Показать заголовок"""
        self.clear_screen()
        print("=" * 60)
        print(f"{' ' * 20}AUTO LOGIN v{self.version}")
        print("=" * 60)
        print("Автоматический вход на образовательный портал")
        print("=" * 60)
        print()
    
    def load_config(self):
        """Загрузка конфигурации"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def save_config(self, username, password):
        """Сохранение конфигурации"""
        config = {
            "username": username,
            "password": password,
            "saved": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def get_credentials(self):
        """Получение учетных данных"""
        # Пробуем загрузить сохраненные
        config = self.load_config()
        if config:
            print("✓ Найдены сохраненные данные")
            print(f"  Логин: {config['username']}")
            print(f"  Пароль: {'*' * 8}")
            
            use = input("\nИспользовать эти данные? (y/n): ").lower().strip()
            if use == 'y':
                return config['username'], config['password']
        
        # Запрашиваем новые
        print("\n" + "-" * 40)
        print("ВВЕДИТЕ УЧЕТНЫЕ ДАННЫЕ")
        print("-" * 40)
        
        username = input("\nВведите логин: ").strip()
        while not username:
            print("❌ Логин не может быть пустым!")
            username = input("Введите логин: ").strip()
        
        # Для пароля используем input (в EXE это будет нормально работать)
        password = input("Введите пароль: ").strip()
        while not password:
            print("❌ Пароль не может быть пустым!")
            password = input("Введите пароль: ").strip()
        
        # Предлагаем сохранить
        save = input("\nСохранить данные для будущих запусков? (y/n): ").lower().strip()
        if save == 'y':
            if self.save_config(username, password):
                print("✓ Данные сохранены")
            else:
                print("⚠️  Не удалось сохранить данные")
        
        return username, password
    
    def setup_chrome(self):
        """Настройка Chrome"""
        if not HAS_SELENIUM:
            raise ImportError("Selenium не установлен!")
        
        try:
            # Автоматическая установка ChromeDriver
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.log("ChromeDriver установлен автоматически")
        except:
            self.log("Использую системный ChromeDriver")
            service = None
        
        # Настройка опций
        options = Options()
        
        # Основные опции
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent Windows 11
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Для работы в фоновом режиме (опционально)
        # options.add_argument("--headless")  # Раскомментировать для скрытого режима
        
        return options, service
    
    def perform_login(self, username, password):
        """Выполнение входа"""
        self.log(f"Начинаю вход для пользователя: {username}")
        
        driver = None
        try:
            # Настраиваем Chrome
            options, service = self.setup_chrome()
            
            # Запускаем браузер
            self.log("Запускаю Chrome...")
            if service:
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
            
            # Открываем сайт
            self.log(f"Открываю {self.website}")
            driver.get(self.website)
            
            # Ждем загрузки
            time.sleep(5)
            
            # Экранируем данные для JS
            safe_user = username.replace("'", "\\'").replace('"', '\\"')
            safe_pass = password.replace("'", "\\'").replace('"', '\\"')
            
            # JavaScript для входа
            js_script = f"""
            // Поиск полей ввода
            function setValue(selectors, value) {{
                for (var selector of selectors) {{
                    var element = document.querySelector(selector);
                    if (element) {{
                        element.value = value;
                        element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return true;
                    }}
                }}
                return false;
            }}
            
            // Поля логина
            var loginSelectors = [
                '#login',
                '#username',
                'input[name="login"]',
                'input[name="username"]',
                'input[type="text"]',
                'input[type="email"]'
            ];
            
            // Поля пароля
            var passSelectors = [
                '#password',
                '#pass',
                'input[name="password"]',
                'input[type="password"]'
            ];
            
            // Заполняем
            var loginOk = setValue(loginSelectors, '{safe_user}');
            var passOk = setValue(passSelectors, '{safe_pass}');
            
            if (loginOk && passOk) {{
                // Ищем кнопку
                var buttonSelectors = [
                    'button[type="submit"]',
                    '.btn-login',
                    '.login-button',
                    'input[type="submit"]',
                    '.btn-primary'
                ];
                
                for (var selector of buttonSelectors) {{
                    var btn = document.querySelector(selector);
                    if (btn) {{
                        btn.click();
                        return "Форма отправлена";
                    }}
                }}
                
                // Если кнопку не нашли, пробуем отправить форму
                var forms = document.getElementsByTagName('form');
                if (forms.length > 0) {{
                    forms[0].submit();
                    return "Форма отправлена (через form.submit())";
                }}
                
                return "Поля заполнены, но кнопка не найдена";
            }} else {{
                return "Не удалось найти все поля для ввода";
            }}
            """
            
            # Выполняем скрипт
            result = driver.execute_script(js_script)
            self.log(f"Результат JavaScript: {result}")
            
            # Ждем
            time.sleep(3)
            
            # Проверяем результат
            current_url = driver.current_url
            page_title = driver.title
            
            self.log(f"Текущий URL: {current_url}")
            self.log(f"Заголовок страницы: {page_title}")
            
            # Анализируем результат
            success_keywords = ['dashboard', 'main', 'profile', 'личный кабинет', 'успешный вход']
            failure_keywords = ['login', 'auth', 'ошибка', 'error', 'неверный']
            
            success = any(keyword in current_url.lower() for keyword in success_keywords) or \
                     any(keyword in page_title.lower() for keyword in success_keywords)
            
            if success:
                print("\n" + "="*50)
                print("🎉 ВХОД ВЫПОЛНЕН УСПЕШНО!")
                print("="*50)
            else:
                print("\n" + "="*50)
                print("⚠️  ВНИМАНИЕ: Проверьте результат входа")
                print("="*50)
            
            print(f"\n📊 Статус: {result}")
            print(f"🌐 Страница: {current_url[:80]}...")
            print(f"📝 Заголовок: {page_title}")
            
            print("\n" + "="*50)
            print("🖥️  Браузер остается открытым")
            print("📋 Для выхода закройте это окно или нажмите Enter")
            print("="*50)
            
            # Ожидание закрытия
            input("\nНажмите Enter для выхода...")
            
            return True
            
        except Exception as e:
            self.log(f"Ошибка при выполнении входа: {str(e)}")
            print(f"\n❌ ОШИБКА: {str(e)}")
            traceback.print_exc()
            return False
            
        finally:
            if driver:
                try:
                    driver.quit()
                    self.log("Браузер закрыт")
                except:
                    pass
    
    def run(self):
        """Основной запуск"""
        self.show_header()
        
        # Проверяем Selenium
        if not HAS_SELENIUM:
            print("❌ Требуется установить Selenium!")
            print("Запустите: pip install selenium")
            input("\nНажмите Enter для выхода...")
            return
        
        # Получаем учетные данные
        username, password = self.get_credentials()
        
        # Выполняем вход
        print("\n" + "="*60)
        print("🚀 ЗАПУСК АВТОМАТИЧЕСКОГО ВХОДА")
        print("="*60)
        
        self.perform_login(username, password)
        
        print("\n" + "="*60)
        print("👋 ПРОГРАММА ЗАВЕРШЕНА")
        print("="*60)

def main():
    """Точка входа"""
    try:
        app = AutoLoginApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()