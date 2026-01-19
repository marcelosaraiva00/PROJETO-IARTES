"""
CENÁRIOS DE TESTE PARA SMARTPHONES MOTOROLA
Base de testes realistas para treinamento do modelo de ML

Módulos cobertos:
- Câmera (foto, vídeo, modos)
- Conectividade (WiFi, Bluetooth, 4G/5G, NFC)
- Bateria e Energia
- Chamadas e Mensagens
- Apps Nativos (Galeria, Mensagens, Contatos)
- Sistema Operacional
- Segurança (Biometria, PIN, Criptografia)
- Multimídia (Áudio, Vídeo)
- Gestos e Atalhos Moto
- Performance e Armazenamento
"""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from datetime import datetime
from src.models.test_case import TestCase, Action, ActionType, ActionImpact
from src.recommender.ml_recommender import MLTestRecommender


def criar_testes_motorola():
    """Cria suite completa de testes para smartphones Motorola"""
    
    testes = []
    
    # ========================================================================
    # MÓDULO: SETUP E CONFIGURAÇÃO INICIAL
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_SETUP_001",
        name="Configuração Inicial do Dispositivo",
        description="Verifica processo de setup inicial do smartphone Motorola",
        priority=5,
        module="Setup",
        tags={"setup", "initial", "critical"},
        actions=[
            Action(
                id="SETUP_A001",
                description="Ligar o dispositivo pela primeira vez",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=15.0,
                postconditions={"device_on", "welcome_screen"}
            ),
            Action(
                id="SETUP_A002",
                description="Selecionar idioma Português (Brasil)",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"welcome_screen"},
                postconditions={"language_set"}
            ),
            Action(
                id="SETUP_A003",
                description="Conectar à rede WiFi",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"language_set"},
                postconditions={"wifi_connected"}
            ),
            Action(
                id="SETUP_A004",
                description="Fazer login com Google Account",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=20.0,
                preconditions={"wifi_connected"},
                postconditions={"google_logged_in"}
            ),
            Action(
                id="SETUP_A005",
                description="Verificar setup concluído na tela inicial",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"google_logged_in"},
                postconditions={"setup_complete"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: CÂMERA - FOTOGRAFIA
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_CAM_001",
        name="Captura de Foto Modo Normal",
        description="Testa captura de foto no modo normal da câmera",
        priority=5,
        module="Camera",
        tags={"camera", "photo", "smoke"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="CAM_A001",
                description="Abrir aplicativo Câmera",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"camera_app_open"}
            ),
            Action(
                id="CAM_A002",
                description="Verificar modo Foto selecionado",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"camera_app_open"},
                postconditions={"photo_mode_active"}
            ),
            Action(
                id="CAM_A003",
                description="Tirar foto com botão de captura",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"photo_mode_active"},
                postconditions={"photo_captured"}
            ),
            Action(
                id="CAM_A004",
                description="Verificar miniatura da foto na galeria",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"photo_captured"},
                postconditions={"photo_saved"}
            ),
        ]
    ))
    
    testes.append(TestCase(
        id="MOTO_CAM_002",
        name="Câmera Modo Retrato (Portrait)",
        description="Testa modo retrato com efeito de desfoque de fundo",
        priority=4,
        module="Camera",
        tags={"camera", "portrait", "bokeh"},
        dependencies={"MOTO_CAM_001"},
        actions=[
            Action(
                id="CAM_A005",
                description="Alternar para modo Retrato",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"camera_app_open"},
                postconditions={"portrait_mode_active"}
            ),
            Action(
                id="CAM_A006",
                description="Posicionar pessoa no enquadramento",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"portrait_mode_active"},
                postconditions={"subject_framed"}
            ),
            Action(
                id="CAM_A007",
                description="Capturar foto em modo retrato",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"subject_framed"},
                postconditions={"portrait_captured"}
            ),
            Action(
                id="CAM_A008",
                description="Verificar efeito bokeh aplicado",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=4.0,
                preconditions={"portrait_captured"},
                postconditions={"bokeh_verified"}
            ),
        ]
    ))
    
    testes.append(TestCase(
        id="MOTO_CAM_003",
        name="Gravação de Vídeo Full HD",
        description="Testa gravação de vídeo em resolução 1080p",
        priority=4,
        module="Camera",
        tags={"camera", "video", "recording"},
        dependencies={"MOTO_CAM_001"},
        actions=[
            Action(
                id="CAM_A009",
                description="Alternar para modo Vídeo",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"camera_app_open"},
                postconditions={"video_mode_active"}
            ),
            Action(
                id="CAM_A010",
                description="Configurar resolução 1080p",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=4.0,
                preconditions={"video_mode_active"},
                postconditions={"resolution_1080p"}
            ),
            Action(
                id="CAM_A011",
                description="Iniciar gravação de vídeo",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"resolution_1080p"},
                postconditions={"recording_started"}
            ),
            Action(
                id="CAM_A012",
                description="Gravar por 10 segundos",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"recording_started"},
                postconditions={"video_recorded"}
            ),
            Action(
                id="CAM_A013",
                description="Parar gravação",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"video_recorded"},
                postconditions={"recording_stopped"}
            ),
            Action(
                id="CAM_A014",
                description="Verificar vídeo salvo na galeria",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"recording_stopped"},
                postconditions={"video_saved"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: CONECTIVIDADE - WIFI
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_WIFI_001",
        name="Conexão WiFi 2.4GHz",
        description="Testa conexão com rede WiFi 2.4GHz",
        priority=5,
        module="Connectivity",
        tags={"wifi", "connectivity", "critical"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="WIFI_A001",
                description="Abrir Configurações",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"setup_complete"},
                postconditions={"settings_open"}
            ),
            Action(
                id="WIFI_A002",
                description="Navegar para WiFi",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"settings_open"},
                postconditions={"wifi_settings_open"}
            ),
            Action(
                id="WIFI_A003",
                description="Selecionar rede WiFi 2.4GHz",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"wifi_settings_open"},
                postconditions={"network_selected"}
            ),
            Action(
                id="WIFI_A004",
                description="Inserir senha da rede",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"network_selected"},
                postconditions={"password_entered"}
            ),
            Action(
                id="WIFI_A005",
                description="Verificar conexão estabelecida",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"password_entered"},
                postconditions={"wifi_connected"}
            ),
            Action(
                id="WIFI_A006",
                description="Desconectar e esquecer TODAS as redes salvas (ação destrutiva)",
                action_type=ActionType.DELETION,
                impact=ActionImpact.DESTRUCTIVE,  # Apaga TODAS as redes - DESTRUCTIVE!
                estimated_time=10.0,
                preconditions={"wifi_connected"},
                postconditions={"all_networks_forgotten"}
            ),
        ]
    ))
    
    testes.append(TestCase(
        id="MOTO_WIFI_002",
        name="Navegação Web via WiFi",
        description="Testa navegação em websites com WiFi conectado",
        priority=3,
        module="Connectivity",
        tags={"wifi", "browser", "internet"},
        dependencies={"MOTO_WIFI_001"},
        actions=[
            Action(
                id="WIFI_A006",
                description="Abrir navegador Chrome",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"wifi_connected"},
                postconditions={"browser_open"}
            ),
            Action(
                id="WIFI_A007",
                description="Acessar website de teste (google.com)",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"browser_open"},
                postconditions={"website_loading"}
            ),
            Action(
                id="WIFI_A008",
                description="Verificar página carregada completamente",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"website_loading"},
                postconditions={"page_loaded"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: CONECTIVIDADE - BLUETOOTH
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_BT_001",
        name="Pareamento Bluetooth com Fone",
        description="Testa pareamento com fone de ouvido Bluetooth",
        priority=4,
        module="Connectivity",
        tags={"bluetooth", "audio", "pairing"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="BT_A001",
                description="Ativar Bluetooth nas configurações",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"bluetooth_on"}
            ),
            Action(
                id="BT_A002",
                description="Colocar fone em modo pareamento",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"bluetooth_on"},
                postconditions={"headset_discoverable"}
            ),
            Action(
                id="BT_A003",
                description="Buscar dispositivos disponíveis",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"headset_discoverable"},
                postconditions={"devices_found"}
            ),
            Action(
                id="BT_A004",
                description="Selecionar fone para parear",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"devices_found"},
                postconditions={"pairing_initiated"}
            ),
            Action(
                id="BT_A005",
                description="Verificar pareamento bem-sucedido",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"pairing_initiated"},
                postconditions={"device_paired"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: BATERIA E ENERGIA
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_BAT_001",
        name="Carregamento de Bateria",
        description="Testa processo de carregamento da bateria",
        priority=5,
        module="Battery",
        tags={"battery", "charging", "critical"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="BAT_A001",
                description="Verificar nível atual da bateria",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"setup_complete"},
                postconditions={"battery_level_checked"}
            ),
            Action(
                id="BAT_A002",
                description="Conectar carregador USB-C",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"battery_level_checked"},
                postconditions={"charger_connected"}
            ),
            Action(
                id="BAT_A003",
                description="Verificar ícone de carregamento",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"charger_connected"},
                postconditions={"charging_icon_visible"}
            ),
            Action(
                id="BAT_A004",
                description="Aguardar 1 minuto e verificar incremento",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=60.0,
                preconditions={"charging_icon_visible"},
                postconditions={"battery_charging"}
            ),
        ]
    ))
    
    testes.append(TestCase(
        id="MOTO_BAT_002",
        name="Modo Economia de Bateria",
        description="Testa ativação do modo economia de bateria",
        priority=3,
        module="Battery",
        tags={"battery", "power_saving"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="BAT_A005",
                description="Abrir configurações de bateria",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"battery_settings_open"}
            ),
            Action(
                id="BAT_A006",
                description="Ativar Economia de Bateria",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"battery_settings_open"},
                postconditions={"power_saver_on"}
            ),
            Action(
                id="BAT_A007",
                description="Verificar indicador visual no status bar",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"power_saver_on"},
                postconditions={"power_saver_active"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: CHAMADAS E TELEFONIA
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_CALL_001",
        name="Realizar Chamada de Voz",
        description="Testa realização de chamada de voz normal",
        priority=5,
        module="Telephony",
        tags={"call", "voice", "critical"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="CALL_A001",
                description="Abrir aplicativo Telefone",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"setup_complete"},
                postconditions={"phone_app_open"}
            ),
            Action(
                id="CALL_A002",
                description="Digitar número de teste",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"phone_app_open"},
                postconditions={"number_entered"}
            ),
            Action(
                id="CALL_A003",
                description="Iniciar chamada",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"number_entered"},
                postconditions={"call_initiated"}
            ),
            Action(
                id="CALL_A004",
                description="Verificar tela de chamada ativa",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"call_initiated"},
                postconditions={"call_active"}
            ),
            Action(
                id="CALL_A005",
                description="Encerrar chamada",
                action_type=ActionType.DELETION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"call_active"},
                postconditions={"call_ended"}
            ),
        ]
    ))
    
    testes.append(TestCase(
        id="MOTO_CALL_002",
        name="Receber Chamada",
        description="Testa recebimento e atendimento de chamada",
        priority=5,
        module="Telephony",
        tags={"call", "incoming", "critical"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="CALL_A006",
                description="Aguardar chamada de entrada",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"setup_complete"},
                postconditions={"incoming_call"}
            ),
            Action(
                id="CALL_A007",
                description="Verificar tela de chamada recebida",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"incoming_call"},
                postconditions={"call_screen_displayed"}
            ),
            Action(
                id="CALL_A008",
                description="Atender chamada (swipe)",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"call_screen_displayed"},
                postconditions={"call_answered"}
            ),
            Action(
                id="CALL_A009",
                description="Verificar áudio da chamada",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"call_answered"},
                postconditions={"audio_working"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: MENSAGENS (SMS)
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_SMS_001",
        name="Enviar SMS",
        description="Testa envio de mensagem SMS",
        priority=4,
        module="Messaging",
        tags={"sms", "messaging"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="SMS_A001",
                description="Abrir app Mensagens",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"setup_complete"},
                postconditions={"messages_app_open"}
            ),
            Action(
                id="SMS_A002",
                description="Criar nova mensagem",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"messages_app_open"},
                postconditions={"new_message_screen"}
            ),
            Action(
                id="SMS_A003",
                description="Inserir número destinatário",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"new_message_screen"},
                postconditions={"recipient_added"}
            ),
            Action(
                id="SMS_A004",
                description="Digitar texto da mensagem",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"recipient_added"},
                postconditions={"message_typed"}
            ),
            Action(
                id="SMS_A005",
                description="Enviar mensagem",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"message_typed"},
                postconditions={"sms_sent"}
            ),
            Action(
                id="SMS_A006",
                description="Verificar mensagem enviada",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"sms_sent"},
                postconditions={"send_confirmed"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: SEGURANÇA - BIOMETRIA
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_SEC_001",
        name="Cadastrar Impressão Digital",
        description="Testa cadastro de impressão digital para desbloqueio",
        priority=4,
        module="Security",
        tags={"security", "biometric", "fingerprint"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="SEC_A001",
                description="Abrir Configurações de Segurança",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"security_settings_open"}
            ),
            Action(
                id="SEC_A002",
                description="Navegar para Impressão Digital",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"security_settings_open"},
                postconditions={"fingerprint_menu"}
            ),
            Action(
                id="SEC_A003",
                description="Iniciar cadastro de digital",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"fingerprint_menu"},
                postconditions={"enrollment_started"}
            ),
            Action(
                id="SEC_A004",
                description="Posicionar dedo no sensor múltiplas vezes",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=30.0,
                preconditions={"enrollment_started"},
                postconditions={"fingerprint_scanned"}
            ),
            Action(
                id="SEC_A005",
                description="Verificar cadastro concluído",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"fingerprint_scanned"},
                postconditions={"fingerprint_enrolled"}
            ),
        ]
    ))
    
    testes.append(TestCase(
        id="MOTO_SEC_002",
        name="Desbloqueio com Impressão Digital",
        description="Testa desbloqueio do aparelho usando digital cadastrada",
        priority=4,
        module="Security",
        tags={"security", "biometric", "unlock"},
        dependencies={"MOTO_SEC_001"},
        actions=[
            Action(
                id="SEC_A006",
                description="Bloquear o dispositivo",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"fingerprint_enrolled"},
                postconditions={"device_locked"}
            ),
            Action(
                id="SEC_A007",
                description="Pressionar botão power para acordar",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"device_locked"},
                postconditions={"lock_screen_visible"}
            ),
            Action(
                id="SEC_A008",
                description="Posicionar dedo no sensor",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"lock_screen_visible"},
                postconditions={"finger_detected"}
            ),
            Action(
                id="SEC_A009",
                description="Verificar desbloqueio bem-sucedido",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"finger_detected"},
                postconditions={"device_unlocked"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: GESTOS MOTO
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_GESTURE_001",
        name="Gesto Chacoalhar para Lanterna",
        description="Testa ativação da lanterna com gesto de chacoalhar",
        priority=3,
        module="MotoGestures",
        tags={"gestures", "moto_actions", "flashlight"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="GEST_A001",
                description="Ativar Moto Actions nas configurações",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"setup_complete"},
                postconditions={"moto_actions_on"}
            ),
            Action(
                id="GEST_A002",
                description="Verificar tela desligada",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"moto_actions_on"},
                postconditions={"screen_off"}
            ),
            Action(
                id="GEST_A003",
                description="Chacoalhar aparelho 2x rapidamente",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"screen_off"},
                postconditions={"shake_detected"}
            ),
            Action(
                id="GEST_A004",
                description="Verificar lanterna ativada",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"shake_detected"},
                postconditions={"flashlight_on"}
            ),
        ]
    ))
    
    testes.append(TestCase(
        id="MOTO_GESTURE_002",
        name="Gesto Girar para Câmera",
        description="Testa abertura rápida da câmera com gesto de girar",
        priority=3,
        module="MotoGestures",
        tags={"gestures", "moto_actions", "camera"},
        dependencies={"MOTO_GESTURE_001"},
        actions=[
            Action(
                id="GEST_A005",
                description="Bloquear o aparelho",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"moto_actions_on"},
                postconditions={"device_locked"}
            ),
            Action(
                id="GEST_A006",
                description="Girar punho 2x rapidamente",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"device_locked"},
                postconditions={"twist_detected"}
            ),
            Action(
                id="GEST_A007",
                description="Verificar câmera aberta",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"twist_detected"},
                postconditions={"camera_opened"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: MULTIMÍDIA - ÁUDIO
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_AUDIO_001",
        name="Reprodução de Música",
        description="Testa reprodução de arquivo de áudio",
        priority=3,
        module="Multimedia",
        tags={"audio", "music", "playback"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="AUDIO_A001",
                description="Abrir app de Música",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"music_app_open"}
            ),
            Action(
                id="AUDIO_A002",
                description="Selecionar uma música",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"music_app_open"},
                postconditions={"track_selected"}
            ),
            Action(
                id="AUDIO_A003",
                description="Reproduzir música",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"track_selected"},
                postconditions={"music_playing"}
            ),
            Action(
                id="AUDIO_A004",
                description="Verificar áudio no alto-falante",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"music_playing"},
                postconditions={"audio_verified"}
            ),
            Action(
                id="AUDIO_A005",
                description="Ajustar volume",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"audio_verified"},
                postconditions={"volume_adjusted"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: PERFORMANCE E ARMAZENAMENTO
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_PERF_001",
        name="Verificar Armazenamento Disponível",
        description="Testa visualização de espaço de armazenamento",
        priority=2,
        module="Performance",
        tags={"storage", "memory"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="PERF_A001",
                description="Abrir Configurações",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"setup_complete"},
                postconditions={"settings_open"}
            ),
            Action(
                id="PERF_A002",
                description="Navegar para Armazenamento",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"settings_open"},
                postconditions={"storage_menu_open"}
            ),
            Action(
                id="PERF_A003",
                description="Verificar espaço total e disponível",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"storage_menu_open"},
                postconditions={"storage_info_displayed"}
            ),
            Action(
                id="PERF_A004",
                description="Limpar cache de todos os apps (ação destrutiva)",
                action_type=ActionType.DELETION,
                impact=ActionImpact.DESTRUCTIVE,  # Limpa TODOS os caches - DESTRUCTIVE!
                estimated_time=15.0,
                preconditions={"storage_info_displayed"},
                postconditions={"cache_cleared"}
            ),
        ]
    ))
    
    testes.append(TestCase(
        id="MOTO_PERF_002",
        name="Multitarefa - Trocar Apps",
        description="Testa alternância entre múltiplos apps abertos",
        priority=3,
        module="Performance",
        tags={"multitasking", "performance", "apps"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="PERF_A004",
                description="Abrir app 1 (Câmera)",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"app1_open"}
            ),
            Action(
                id="PERF_A005",
                description="Ir para tela inicial (home)",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"app1_open"},
                postconditions={"on_home_screen"}
            ),
            Action(
                id="PERF_A006",
                description="Abrir app 2 (Chrome)",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"on_home_screen"},
                postconditions={"app2_open"}
            ),
            Action(
                id="PERF_A007",
                description="Abrir menu multitarefa",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"app2_open"},
                postconditions={"recents_open"}
            ),
            Action(
                id="PERF_A008",
                description="Trocar para app 1 (Câmera)",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"recents_open"},
                postconditions={"switched_to_app1"}
            ),
            Action(
                id="PERF_A009",
                description="Verificar app manteve estado",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"switched_to_app1"},
                postconditions={"state_preserved"}
            ),
        ]
    ))
    
    # ========================================================================
    # MÓDULO: DISPLAY E TELA
    # ========================================================================
    
    testes.append(TestCase(
        id="MOTO_DISP_001",
        name="Ajustar Brilho da Tela",
        description="Testa ajuste manual de brilho do display",
        priority=2,
        module="Display",
        tags={"display", "brightness"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="DISP_A001",
                description="Deslizar barra de notificações",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"setup_complete"},
                postconditions={"notification_panel_open"}
            ),
            Action(
                id="DISP_A002",
                description="Verificar controle de brilho visível",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"notification_panel_open"},
                postconditions={"brightness_slider_visible"}
            ),
            Action(
                id="DISP_A003",
                description="Ajustar brilho para 50%",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"brightness_slider_visible"},
                postconditions={"brightness_adjusted"}
            ),
            Action(
                id="DISP_A004",
                description="Verificar mudança visual no brilho",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"brightness_adjusted"},
                postconditions={"brightness_changed"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: CONECTIVIDADE - DADOS MÓVEIS / 4G/5G
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_CELL_001",
        name="Ativar Dados Móveis e Verificar Conectividade",
        description="Testa ativação de dados móveis e valida conectividade (indicador 4G/5G e navegação simples).",
        priority=5,
        module="Connectivity",
        tags={"cellular", "mobile_data", "4g", "5g", "critical"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="CELL_A001",
                description="Abrir Configurações",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"setup_complete"},
                postconditions={"settings_open"}
            ),
            Action(
                id="CELL_A002",
                description="Navegar para Rede e Internet / SIM",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"settings_open"},
                postconditions={"cellular_settings_open"}
            ),
            Action(
                id="CELL_A003",
                description="Ativar Dados móveis",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"cellular_settings_open"},
                postconditions={"mobile_data_on"}
            ),
            Action(
                id="CELL_A004",
                description="Verificar indicador de rede (4G/5G/LTE) na barra de status",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"mobile_data_on"},
                postconditions={"cellular_indicator_visible"}
            ),
            Action(
                id="CELL_A005",
                description="Abrir Chrome e carregar um site de teste",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=8.0,
                preconditions={"mobile_data_on"},
                postconditions={"cellular_browsing_ok"}
            ),
        ]
    ))

    testes.append(TestCase(
        id="MOTO_CELL_002",
        name="Alternar Modo Avião",
        description="Testa ativação/desativação do modo avião e impacto em conectividade.",
        priority=4,
        module="Connectivity",
        tags={"airplane_mode", "cellular", "wifi", "bluetooth"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="CELL_A006",
                description="Abrir painel rápido (quick settings)",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"setup_complete"},
                postconditions={"quick_settings_open"}
            ),
            Action(
                id="CELL_A007",
                description="Ativar Modo Avião",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"quick_settings_open"},
                postconditions={"airplane_mode_on"}
            ),
            Action(
                id="CELL_A008",
                description="Verificar que sinal celular e WiFi estão desligados",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=4.0,
                preconditions={"airplane_mode_on"},
                postconditions={"radios_off_verified"}
            ),
            Action(
                id="CELL_A009",
                description="Desativar Modo Avião",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"airplane_mode_on"},
                postconditions={"airplane_mode_off"}
            ),
            Action(
                id="CELL_A010",
                description="Verificar retorno do sinal e conectividade",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=8.0,
                preconditions={"airplane_mode_off"},
                postconditions={"radios_on_verified"}
            ),
        ]
    ))

    testes.append(TestCase(
        id="MOTO_CELL_003",
        name="Ativar Hotspot Wi-Fi (Tethering)",
        description="Testa ativação do hotspot e verificação de SSID/senha (sem exigir segundo dispositivo).",
        priority=3,
        module="Connectivity",
        tags={"hotspot", "tethering", "wifi"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="CELL_A011",
                description="Abrir Configurações de Hotspot e Tethering",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=4.0,
                preconditions={"setup_complete"},
                postconditions={"hotspot_settings_open"}
            ),
            Action(
                id="CELL_A012",
                description="Configurar nome do hotspot (SSID) e senha",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=8.0,
                preconditions={"hotspot_settings_open"},
                postconditions={"hotspot_configured"}
            ),
            Action(
                id="CELL_A013",
                description="Ativar Hotspot Wi-Fi",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"hotspot_configured"},
                postconditions={"hotspot_on"}
            ),
            Action(
                id="CELL_A014",
                description="Verificar indicador de hotspot ativo",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"hotspot_on"},
                postconditions={"hotspot_active_verified"}
            ),
            Action(
                id="CELL_A015",
                description="Desativar Hotspot Wi-Fi",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"hotspot_on"},
                postconditions={"hotspot_off"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: LOCALIZAÇÃO / GPS
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_GPS_001",
        name="Ativar Localização e Obter Fix de GPS",
        description="Testa ativação de localização e obtenção de posição em app de mapas.",
        priority=4,
        module="Location",
        tags={"gps", "location", "maps"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="GPS_A001",
                description="Abrir Configurações e entrar em Localização",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=4.0,
                preconditions={"setup_complete"},
                postconditions={"location_settings_open"}
            ),
            Action(
                id="GPS_A002",
                description="Ativar Localização",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"location_settings_open"},
                postconditions={"location_on"}
            ),
            Action(
                id="GPS_A003",
                description="Abrir app de Mapas e solicitar localização atual",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"location_on"},
                postconditions={"maps_open"}
            ),
            Action(
                id="GPS_A004",
                description="Verificar fix/precisão de localização exibida",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=12.0,
                preconditions={"maps_open"},
                postconditions={"gps_fix_verified"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: NFC
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_NFC_001",
        name="Ativar NFC",
        description="Testa ativação do NFC e valida que o toggle fica ativo.",
        priority=3,
        module="NFC",
        tags={"nfc", "payments", "tap"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="NFC_A001",
                description="Abrir Configurações e entrar em Conexões/NFC",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"setup_complete"},
                postconditions={"nfc_settings_open"}
            ),
            Action(
                id="NFC_A002",
                description="Ativar NFC",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"nfc_settings_open"},
                postconditions={"nfc_on"}
            ),
            Action(
                id="NFC_A003",
                description="Verificar indicador NFC ativado nas configurações",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"nfc_on"},
                postconditions={"nfc_verified"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: SISTEMA / ATUALIZAÇÃO / REINICIALIZAÇÃO
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_SYS_001",
        name="Verificar Atualizações do Sistema",
        description="Testa fluxo de checagem de atualização OTA (sem aplicar update).",
        priority=3,
        module="System",
        tags={"ota", "update", "system"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="SYS_A001",
                description="Abrir Configurações e entrar em Sistema",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=4.0,
                preconditions={"setup_complete"},
                postconditions={"system_settings_open"}
            ),
            Action(
                id="SYS_A002",
                description="Abrir Atualização do sistema",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"system_settings_open"},
                postconditions={"system_update_screen"}
            ),
            Action(
                id="SYS_A003",
                description="Executar verificação de atualizações",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=12.0,
                preconditions={"system_update_screen"},
                postconditions={"update_check_done"}
            ),
            Action(
                id="SYS_A004",
                description="Verificar resultado da checagem (atualizado ou update disponível)",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"update_check_done"},
                postconditions={"update_status_verified"}
            ),
        ]
    ))

    testes.append(TestCase(
        id="MOTO_SYS_002",
        name="Reiniciar Dispositivo e Validar Boot",
        description="Testa reinicialização do dispositivo e retorno à tela inicial.",
        priority=4,
        module="System",
        tags={"reboot", "stability"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="SYS_A005",
                description="Abrir menu de energia (Power) e selecionar Reiniciar",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"setup_complete"},
                postconditions={"reboot_initiated"}
            ),
            Action(
                id="SYS_A006",
                description="Aguardar boot completar e desbloquear (se necessário)",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=35.0,
                preconditions={"reboot_initiated"},
                postconditions={"device_booted"}
            ),
            Action(
                id="SYS_A007",
                description="Verificar acesso à tela inicial após boot",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=4.0,
                preconditions={"device_booted"},
                postconditions={"home_after_reboot"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: NOTIFICAÇÕES / SOM / VIBRAÇÃO
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_NOTIF_001",
        name="Notificação - Som e Vibração",
        description="Testa recebimento de notificação (simulada) e comportamento de som/vibração.",
        priority=3,
        module="Notifications",
        tags={"notification", "sound", "vibration"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="NOTIF_A001",
                description="Abrir Configurações de Som e Vibração",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=4.0,
                preconditions={"setup_complete"},
                postconditions={"sound_settings_open"}
            ),
            Action(
                id="NOTIF_A002",
                description="Ajustar volume de notificações para nível médio",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"sound_settings_open"},
                postconditions={"notification_volume_set"}
            ),
            Action(
                id="NOTIF_A003",
                description="Gerar/receber uma notificação (ex: mensagem de teste) e observar comportamento",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"notification_volume_set"},
                postconditions={"notification_received"}
            ),
            Action(
                id="NOTIF_A004",
                description="Abrir painel de notificações e limpar notificação",
                action_type=ActionType.DELETION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"notification_received"},
                postconditions={"notification_cleared"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: ACESSIBILIDADE
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_ACC_001",
        name="Ativar TalkBack e Navegar",
        description="Testa ativação do TalkBack e navegação básica; desativa ao final.",
        priority=2,
        module="Accessibility",
        tags={"accessibility", "talkback"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="ACC_A001",
                description="Abrir Configurações e entrar em Acessibilidade",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"setup_complete"},
                postconditions={"accessibility_settings_open"}
            ),
            Action(
                id="ACC_A002",
                description="Ativar TalkBack",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"accessibility_settings_open"},
                postconditions={"talkback_on"}
            ),
            Action(
                id="ACC_A003",
                description="Validar leitura de elementos na tela inicial (toque simples e duplo toque)",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=12.0,
                preconditions={"talkback_on"},
                postconditions={"talkback_navigation_verified"}
            ),
            Action(
                id="ACC_A004",
                description="Desativar TalkBack",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"talkback_on"},
                postconditions={"talkback_off"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: SENSORES / ROTAÇÃO AUTOMÁTICA
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_SENSOR_001",
        name="Rotação Automática (Acelerômetro/Giroscópio)",
        description="Testa rotação automática da tela em um app compatível (ex: navegador).",
        priority=2,
        module="Sensors",
        tags={"rotation", "sensors", "gyro"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="SENS_A001",
                description="Abrir painel rápido e ativar Rotação automática",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"auto_rotate_on"}
            ),
            Action(
                id="SENS_A002",
                description="Abrir navegador (ou app de fotos) e girar o aparelho para paisagem",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"auto_rotate_on"},
                postconditions={"rotation_triggered"}
            ),
            Action(
                id="SENS_A003",
                description="Verificar que a interface girou para paisagem e retorna para retrato",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"rotation_triggered"},
                postconditions={"rotation_verified"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: MULTIMÍDIA - GRAVAÇÃO DE ÁUDIO
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_AUDIO_002",
        name="Gravar e Reproduzir Áudio",
        description="Testa gravação de áudio (gravador) e reprodução do arquivo salvo.",
        priority=3,
        module="Multimedia",
        tags={"audio", "recording", "mic"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="AUD2_A001",
                description="Abrir app Gravador de Áudio",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"recorder_open"}
            ),
            Action(
                id="AUD2_A002",
                description="Iniciar gravação e falar por 5 segundos",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=7.0,
                preconditions={"recorder_open"},
                postconditions={"audio_recorded"}
            ),
            Action(
                id="AUD2_A003",
                description="Parar gravação e salvar",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"audio_recorded"},
                postconditions={"audio_saved"}
            ),
            Action(
                id="AUD2_A004",
                description="Reproduzir gravação e verificar áudio audível",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=8.0,
                preconditions={"audio_saved"},
                postconditions={"audio_playback_verified"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: ARMAZENAMENTO / CAPTURA DE TELA
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_STORE_001",
        name="Capturar Screenshot e Verificar Salvo",
        description="Testa captura de screenshot e verificação na galeria/fotos.",
        priority=2,
        module="Storage",
        tags={"screenshot", "gallery", "storage"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="STORE_A001",
                description="Abrir uma tela de referência (ex: Configurações) para capturar",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"setup_complete"},
                postconditions={"reference_screen_open"}
            ),
            Action(
                id="STORE_A002",
                description="Capturar screenshot (Power + Volume Down)",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=2.0,
                preconditions={"reference_screen_open"},
                postconditions={"screenshot_taken"}
            ),
            Action(
                id="STORE_A003",
                description="Abrir Galeria/Fotos e localizar screenshot",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"screenshot_taken"},
                postconditions={"gallery_open"}
            ),
            Action(
                id="STORE_A004",
                description="Verificar screenshot visível e acessível",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=3.0,
                preconditions={"gallery_open"},
                postconditions={"screenshot_verified"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: SEGURANÇA - PIN
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_SEC_003",
        name="Configurar PIN e Desbloquear",
        description="Testa configuração de bloqueio por PIN e desbloqueio na tela de bloqueio.",
        priority=3,
        module="Security",
        tags={"security", "pin", "lockscreen"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="PIN_A001",
                description="Abrir Configurações de Segurança e entrar em Bloqueio de Tela",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"setup_complete"},
                postconditions={"lock_settings_open"}
            ),
            Action(
                id="PIN_A002",
                description="Definir PIN de 4-6 dígitos",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=10.0,
                preconditions={"lock_settings_open"},
                postconditions={"pin_set"}
            ),
            Action(
                id="PIN_A003",
                description="Bloquear o dispositivo",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=1.0,
                preconditions={"pin_set"},
                postconditions={"device_locked"}
            ),
            Action(
                id="PIN_A004",
                description="Desbloquear com PIN e verificar acesso à tela inicial",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=6.0,
                preconditions={"device_locked"},
                postconditions={"pin_unlock_verified"}
            ),
        ]
    ))

    # ========================================================================
    # MÓDULO: APPS - PLAY STORE (INSTALAR/ABRIR/DESINSTALAR)
    # ========================================================================

    testes.append(TestCase(
        id="MOTO_APP_001",
        name="Instalar e Desinstalar App (Play Store)",
        description="Testa fluxo de instalar um app leve, abrir e desinstalar.",
        priority=3,
        module="Apps",
        tags={"play_store", "install", "uninstall"},
        dependencies={"MOTO_SETUP_001"},
        actions=[
            Action(
                id="APP_A001",
                description="Abrir Play Store",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=5.0,
                preconditions={"google_logged_in"},
                postconditions={"play_store_open"}
            ),
            Action(
                id="APP_A002",
                description="Buscar por um app leve de teste (ex: 'Calculadora')",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=8.0,
                preconditions={"play_store_open"},
                postconditions={"app_search_done"}
            ),
            Action(
                id="APP_A003",
                description="Instalar o app selecionado",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                estimated_time=25.0,
                preconditions={"app_search_done"},
                postconditions={"app_installed"}
            ),
            Action(
                id="APP_A004",
                description="Abrir o app instalado e verificar abertura",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                estimated_time=8.0,
                preconditions={"app_installed"},
                postconditions={"app_open_verified"}
            ),
            Action(
                id="APP_A005",
                description="Desinstalar o app (Configurações > Apps)",
                action_type=ActionType.DELETION,
                impact=ActionImpact.DESTRUCTIVE,  # CORRIGIDO: desinstalar é destrutivo
                estimated_time=12.0,
                preconditions={"app_installed"},
                postconditions={"app_uninstalled"}
            ),
        ]
    ))
    
    return testes


# ============================================================================
# EXECUTAR SISTEMA COM TESTES MOTOROLA
# ============================================================================

def main():
    # Configurar encoding UTF-8 para Windows
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 80)
    print("SISTEMA DE RECOMENDAÇÃO - TESTES MOTOROLA")
    print("=" * 80)
    print()
    
    # Carregar testes
    print("📱 Carregando casos de teste Motorola...")
    testes = criar_testes_motorola()
    print(f"✓ {len(testes)} testes carregados")
    print()
    
    # Estatísticas
    modulos = set(t.module for t in testes)
    total_acoes = sum(len(t.actions) for t in testes)
    tempo_total = sum(t.get_total_estimated_time() for t in testes)
    
    print("📊 Estatísticas da Suíte:")
    print(f"  • Total de testes: {len(testes)}")
    print(f"  • Módulos cobertos: {len(modulos)}")
    print(f"  • Total de ações: {total_acoes}")
    print(f"  • Tempo estimado total: {tempo_total/60:.1f} minutos")
    print()
    
    print("🎯 Módulos inclusos:")
    for modulo in sorted(modulos):
        qtd = sum(1 for t in testes if t.module == modulo)
        print(f"  • {modulo}: {qtd} testes")
    print()
    
    # Criar recomendador
    print("🤖 Inicializando recomendador...")
    recommender = MLTestRecommender()
    
    try:
        recommender.load_model("models/motorola_modelo.pkl")
        print(f"✓ Modelo existente carregado ({len(recommender.feedback_history)} feedbacks)")
    except:
        print("✓ Novo modelo criado")
    print()
    
    # Obter recomendação
    print("🎯 Gerando recomendação de execução...")
    recomendacao = recommender.recommend_order(testes)
    
    print(f"\n📊 RECOMENDAÇÃO:")
    print(f"  Confiança: {recomendacao.confidence_score:.1%}")
    print(f"  Tempo total estimado: {recomendacao.estimated_total_time/60:.1f} minutos")
    print(f"  Resets estimados: {recomendacao.estimated_resets}")
    print(f"  Método: {recomendacao.reasoning.get('method', 'N/A')}")
    print()
    
    print("📝 Ordem sugerida de execução:")
    print()
    
    modulo_atual = None
    for idx, test_id in enumerate(recomendacao.recommended_order, 1):
        teste = next(tc for tc in testes if tc.id == test_id)
        
        # Separar por módulo
        if teste.module != modulo_atual:
            if modulo_atual is not None:
                print()
            print(f"  [{teste.module}]")
            modulo_atual = teste.module
        
        destrutivo = "🔴" if teste.has_destructive_actions() else "🟢"
        print(f"    {idx:2d}. {destrutivo} {teste.id} - {teste.name}")
        print(f"        ├─ Prioridade: {teste.priority} | Ações: {len(teste.actions)} | " +
              f"Tempo: {teste.get_total_estimated_time():.0f}s")
    
    print()
    print("=" * 80)
    print("💾 Salvando modelo...")
    recommender.save_model("models/motorola_modelo.pkl")
    print("✓ Modelo salvo: models/motorola_modelo.pkl")
    print()
    
    print("=" * 80)
    print("✅ SUÍTE DE TESTES MOTOROLA PRONTA!")
    print("=" * 80)
    print()
    print("📚 Para treinar o modelo:")
    print("  1. Execute estes testes na ordem sugerida")
    print("  2. Use template_meus_testes.py para dar feedback")
    print("  3. Ou rode advanced_training.py para treinamento automático")
    print()
    print("🎓 Arquivos criados:")
    print("  • testes_motorola.py - Este arquivo (suíte completa)")
    print("  • models/motorola_modelo.pkl - Modelo inicial")
    print()


if __name__ == "__main__":
    main()
