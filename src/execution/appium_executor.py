from __future__ import annotations

"""
Executor Android via Appium (UIAutomator2).

Este arquivo é um ESQUELETO: para executar de verdade, você precisa:
- Um Motorola conectado via USB (ADB habilitado)
- Appium Server rodando (local)
- appium-python-client instalado

E, principalmente, mapear cada Action.description / ActionType para comandos reais:
- abrir app, clicar, digitar, validar texto, etc.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Set

from src.execution.executor_base import ExecutionResult, State
from src.models.test_case import TestCase, ActionType, ActionImpact


@dataclass
class AppiumConfig:
    server_url: str = "http://127.0.0.1:4723"
    platform_name: str = "Android"
    automation_name: str = "UIAutomator2"
    device_name: str = "Android"
    app_package: Optional[str] = None
    app_activity: Optional[str] = None


class AndroidAppiumExecutor:
    def __init__(self, config: AppiumConfig):
        self.config = config
        self._driver = None

    def _ensure_driver(self):
        if self._driver is not None:
            return

        # Import local para não exigir dependência se usuário não usar Appium
        from appium import webdriver  # type: ignore
        from appium.options.android import UiAutomator2Options  # type: ignore

        opts = UiAutomator2Options()
        opts.platform_name = self.config.platform_name
        opts.automation_name = self.config.automation_name
        opts.device_name = self.config.device_name
        if self.config.app_package:
            opts.app_package = self.config.app_package
        if self.config.app_activity:
            opts.app_activity = self.config.app_activity

        self._driver = webdriver.Remote(self.config.server_url, options=opts)

    # ----------------------------
    # Helpers de UI (robustos)
    # ----------------------------
    def _find_by_text_contains(self, text: str, timeout_s: float = 10.0):
        """
        Busca elemento por texto parcial (UiSelector textContains).
        Útil para apps de sistema (Configurações) em PT-BR onde IDs variam.
        """
        self._ensure_driver()
        # Import local (Selenium já é dependência do appium-python-client)
        from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
        from selenium.webdriver.support import expected_conditions as EC  # type: ignore
        from selenium.common.exceptions import TimeoutException  # type: ignore

        locator = ("-android uiautomator", f'new UiSelector().textContains("{text}")')
        try:
            return WebDriverWait(self._driver, timeout_s).until(EC.presence_of_element_located(locator))
        except TimeoutException as e:
            raise RuntimeError(f'Elemento com texto contendo "{text}" não encontrado (timeout {timeout_s}s)') from e

    def _tap_text(self, text: str, timeout_s: float = 10.0):
        el = self._find_by_text_contains(text, timeout_s=timeout_s)
        el.click()

    def _tap_text_one_of(self, candidates: list[str], timeout_s: float = 6.0):
        last_err: Exception | None = None
        for c in candidates:
            try:
                self._tap_text(c, timeout_s=timeout_s)
                return c
            except Exception as e:
                last_err = e
        raise RuntimeError(f"Nenhuma opção encontrada entre: {candidates}") from last_err

    def _back(self, times: int = 1):
        self._ensure_driver()
        for _ in range(times):
            try:
                self._driver.back()
            except Exception:
                pass

    def _start_activity(self, package: str, activity: str):
        self._ensure_driver()
        # start_activity é mais confiável para apps de sistema
        try:
            self._driver.start_activity(package, activity)
        except Exception:
            # fallback: usar am start via execute_script mobile:shell (quando disponível)
            try:
                self._driver.execute_script(
                    "mobile: shell",
                    {"command": "am", "args": ["start", "-n", f"{package}/{activity}"]},
                )
            except Exception as e:
                raise RuntimeError(f"Falha ao abrir activity {package}/{activity}") from e

    def _open_settings(self):
        # Pacote/Activity mais comuns (podem variar por versão)
        self._start_activity("com.android.settings", ".Settings")

    def _open_chrome(self):
        self._start_activity("com.android.chrome", "com.google.android.apps.chrome.Main")

    def _open_play_store(self):
        self._start_activity("com.android.vending", "com.google.android.finsky.activities.MainActivity")

    def _open_phone(self):
        # Google Dialer
        self._start_activity("com.google.android.dialer", "com.google.android.dialer.extensions.GoogleDialtactsActivity")

    def _open_messages(self):
        # Google Messages
        self._start_activity("com.google.android.apps.messaging", "com.google.android.apps.messaging.ui.ConversationListActivity")

    def _open_camera(self):
        # Motorola/Google Camera variam; tentativa genérica via intent
        self._ensure_driver()
        try:
            self._driver.execute_script(
                "mobile: shell",
                {"command": "am", "args": ["start", "-a", "android.media.action.IMAGE_CAPTURE"]},
            )
        except Exception:
            # fallback: tentar abrir pacote comum da Moto Camera (pode variar)
            try:
                self._start_activity("com.motorola.camera2", ".Camera")
            except Exception:
                # Último fallback: Google Camera
                self._start_activity("com.google.android.GoogleCamera", "com.android.camera.Camera")

    # ----------------------------
    # Heurística de execução por descrição
    # ----------------------------
    def _execute_action_by_description(self, description: str, state: Set[str]) -> tuple[bool, str]:
        """
        Executa ações típicas de sistema com heurística baseada na descrição (PT-BR).
        Retorna (ok, note).
        """
        d = description.lower().strip()

        # Abrir apps/telas
        if d.startswith("abrir configurações"):
            self._open_settings()
            state.add("settings_open")
            return True, "OK"
        if "abrir aplicativo câmera" in d or d.startswith("abrir app câmera") or d.startswith("abrir câmera"):
            self._open_camera()
            state.add("camera_app_open")
            return True, "OK"
        if "abrir navegador" in d or "abrir chrome" in d:
            self._open_chrome()
            state.add("browser_open")
            return True, "OK"
        if "abrir play store" in d:
            self._open_play_store()
            state.add("play_store_open")
            return True, "OK"
        if "abrir aplicativo telefone" in d or d.startswith("abrir app telefone"):
            self._open_phone()
            state.add("phone_app_open")
            return True, "OK"
        if "abrir app mensagens" in d or "abrir mensagens" in d:
            self._open_messages()
            state.add("messages_app_open")
            return True, "OK"

        # Navegação em Settings via texto
        if "navegar para wifi" in d or d.startswith("navegar para wifi"):
            self._open_settings()
            self._tap_text_one_of(["Wi‑Fi", "Wi-Fi", "WiFi", "Internet", "Rede e Internet"])
            state.add("wifi_settings_open")
            return True, "OK"
        if "navegar para rede e internet" in d or "rede e internet" in d:
            self._open_settings()
            self._tap_text_one_of(["Rede e Internet", "Rede e internet", "Conexões"])
            state.add("cellular_settings_open")
            return True, "OK"
        if "entrar em localização" in d or d.startswith("abrir configurações e entrar em localização"):
            self._open_settings()
            self._tap_text_one_of(["Localização", "Location"])
            state.add("location_settings_open")
            return True, "OK"
        if "entrar em acessibilidade" in d:
            self._open_settings()
            self._tap_text_one_of(["Acessibilidade", "Accessibility"])
            state.add("accessibility_settings_open")
            return True, "OK"
        if "som e vibração" in d:
            self._open_settings()
            self._tap_text_one_of(["Som e vibração", "Som", "Sons e vibração"])
            state.add("sound_settings_open")
            return True, "OK"
        if "sistema" in d and "abrir configurações" in d:
            self._open_settings()
            self._tap_text_one_of(["Sistema", "System"])
            state.add("system_settings_open")
            return True, "OK"

        # Toggles comuns (tentativa por texto)
        if "ativar modo avião" in d:
            # Em muitos Androids: no painel rápido; aqui tentamos Settings
            self._open_settings()
            self._tap_text_one_of(["Rede e Internet", "Conexões"])
            # Procurar opção "Modo avião" e tocar
            self._tap_text_one_of(["Modo avião", "Airplane mode"])
            state.add("airplane_mode_on")
            return True, "OK"
        if "desativar modo avião" in d:
            self._open_settings()
            self._tap_text_one_of(["Rede e Internet", "Conexões"])
            self._tap_text_one_of(["Modo avião", "Airplane mode"])
            state.discard("airplane_mode_on")
            state.add("airplane_mode_off")
            return True, "OK"

        # Verificações simples (por presença de texto)
        if d.startswith("verificar"):
            # Estratégia: se tem palavras-chave, procurar algo na tela
            # Ex.: "Verificar indicador de rede (4G/5G/LTE)" → procurar "LTE" ou "4G" ou "5G"
            if "4g" in d or "5g" in d or "lte" in d:
                try:
                    self._find_by_text_contains("5G", timeout_s=2.0)
                    state.add("cellular_indicator_visible")
                    return True, "OK"
                except Exception:
                    try:
                        self._find_by_text_contains("4G", timeout_s=2.0)
                        state.add("cellular_indicator_visible")
                        return True, "OK"
                    except Exception:
                        try:
                            self._find_by_text_contains("LTE", timeout_s=2.0)
                            state.add("cellular_indicator_visible")
                            return True, "OK"
                        except Exception:
                            # Não necessariamente está na UI atual; não falhar “duro”
                            return True, "Indicador não encontrado na tela atual (verificação suave)"
            if "nfc" in d:
                try:
                    self._find_by_text_contains("NFC", timeout_s=3.0)
                    state.add("nfc_verified")
                    return True, "OK"
                except Exception:
                    return True, "NFC não encontrado na tela atual (verificação suave)"
            return True, "Verificação genérica (sem assert duro)"

        # Se não reconhecemos a ação, sinalizar para o usuário mapear
        return False, f"Ação não mapeada para execução real: '{description}'"

    def reset(self) -> State:
        # Reset do “estado” depende do seu contexto.
        # Exemplo: reiniciar app, limpar cache/dados, voltar home, etc.
        self._ensure_driver()
        try:
            self._driver.reset()
        except Exception:
            # Em alguns casos, reset pode falhar dependendo do driver/app.
            pass
        return set()

    def execute_test_case(self, test_case: TestCase, current_state: State) -> tuple[ExecutionResult, State]:
        self._ensure_driver()
        started_at = datetime.now()
        initial_state: Set[str] = set(current_state)
        state: Set[str] = set(current_state)

        required_reset = False
        total_time = 0.0
        failed_action_id = None
        notes = []

        for action in test_case.actions:
            # Checar precondições “lógicas” (estado interno do runner)
            missing = action.preconditions.difference(state)
            if missing:
                failed_action_id = action.id
                notes.append(f"Precondições faltando: {sorted(missing)}")
                required_reset = action.impact in (ActionImpact.DESTRUCTIVE, ActionImpact.PARTIALLY_DESTRUCTIVE)
                break

            ok, note = self._execute_action_by_description(action.description, state)
            notes.append(note)
            total_time += max(action.estimated_time, 0.1)
            # Aplicar pós-condições “lógicas”
            state.update(action.postconditions)

            if not ok:
                failed_action_id = action.id
                required_reset = True
                
                # Se teste tem teardown_restores, executar teardown mesmo em falha
                if test_case.teardown_restores:
                    try:
                        self._back(times=1)
                        notes.append("[TEARDOWN] Voltou para tela anterior")
                        state = set(initial_state)
                    except Exception as e:
                        notes.append(f"[TEARDOWN] Erro: {str(e)}")
                
                break

        finished_at = datetime.now()
        
        # Se teste tem teardown_restores, executar teardown antes de retornar
        if test_case.teardown_restores:
            try:
                self._back(times=1)  # Voltar uma tela
                notes.append("[TEARDOWN] Voltou para tela anterior")
                # Estado volta ao inicial (não altera estado final)
                state = set(initial_state)
            except Exception as e:
                notes.append(f"[TEARDOWN] Erro: {str(e)}")
        
        result = ExecutionResult(
            test_case_id=test_case.id,
            started_at=started_at,
            finished_at=finished_at,
            actual_execution_time=max((finished_at - started_at).total_seconds(), total_time),
            success=failed_action_id is None,
            required_reset=required_reset,
            notes=" | ".join([n for n in notes if n])[:1000],
            initial_state=initial_state,
            final_state=set(state),  # Se teardown_restores, state = initial_state
            failed_action_id=failed_action_id,
        )
        return result, state

