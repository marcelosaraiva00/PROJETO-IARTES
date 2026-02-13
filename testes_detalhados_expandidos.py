"""
CASOS DE TESTE DETALHADOS E EXPANDIDOS
Baseado no padrão dos testes Dialer - cada ação detalhada em múltiplas ações específicas
Gerado para expandir a cobertura de testes em todas as categorias
"""

from src.models.test_case import TestCase, Action, ActionType, ActionImpact


def criar_testes_detalhados_expandidos():
    """Retorna lista de testes detalhados expandidos para todas as categorias"""
    
    testes = []
    
    # ========================================================================
    # CATEGORIA: CÂMERA - Testes Detalhados
    # ========================================================================
    
    # Teste: Captura de Foto com Flash
    testes.append(TestCase(
        id="CAM-DET-001",
        name="Captura de Foto com Flash Automático",
        description="Captura de foto com flash automático ativado\n\nResultado Esperado: 1- A câmera deve abrir sem erros\n2- O modo flash automático deve estar ativado\n3- A foto deve ser capturada com flash quando necessário\n4- A foto deve ser salva na galeria com qualidade adequada",
        priority=4,
        module="Camera",
        tags={"camera", "photo", "flash", "detailed"},
        validation_point_action="CAM-DET-001_A004",
        actions=[
            Action(
                id="CAM-DET-001_A001",
                description="Abrir aplicativo Câmera",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"camera_app_open"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "navigation"}
            ),
            Action(
                id="CAM-DET-001_A002",
                description="Verificar modo Foto está selecionado",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"camera_app_open"},
                postconditions={"photo_mode_verified"},
                estimated_time=2.0,
                priority=1,
                tags={"camera", "verification"}
            ),
            Action(
                id="CAM-DET-001_A003",
                description="Acessar configurações de flash e selecionar modo Automático",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"photo_mode_verified"},
                postconditions={"flash_auto_enabled"},
                estimated_time=4.0,
                priority=1,
                tags={"camera", "settings"}
            ),
            Action(
                id="CAM-DET-001_A004",
                description="Capturar foto em ambiente com pouca luz",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"flash_auto_enabled"},
                postconditions={"photo_with_flash_captured"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "capture"}
            ),
            Action(
                id="CAM-DET-001_A005",
                description="Verificar flash foi acionado durante captura",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"photo_with_flash_captured"},
                postconditions={"flash_activation_verified"},
                estimated_time=2.0,
                priority=1,
                tags={"camera", "verification"}
            ),
            Action(
                id="CAM-DET-001_A006",
                description="Abrir galeria e verificar foto salva",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"photo_with_flash_captured"},
                postconditions={"photo_saved_in_gallery"},
                estimated_time=4.0,
                priority=1,
                tags={"camera", "gallery"}
            ),
        ]
    ))
    
    # Teste: Zoom Digital durante Gravação de Vídeo
    testes.append(TestCase(
        id="CAM-DET-002",
        name="Gravação de Vídeo com Zoom Digital",
        description="Gravação de vídeo utilizando zoom digital\n\nResultado Esperado: 1- A câmera deve abrir no modo vídeo\n2- O zoom digital deve estar disponível\n3- O vídeo deve ser gravado com zoom aplicado\n4- A qualidade do vídeo deve ser mantida durante zoom\n5- O vídeo deve ser salvo corretamente",
        priority=3,
        module="Camera",
        tags={"camera", "video", "zoom", "detailed"},
        validation_point_action="CAM-DET-002_A005",
        actions=[
            Action(
                id="CAM-DET-002_A001",
                description="Abrir aplicativo Câmera",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"camera_app_open"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "navigation"}
            ),
            Action(
                id="CAM-DET-002_A002",
                description="Alternar para modo Vídeo",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"camera_app_open"},
                postconditions={"video_mode_active"},
                estimated_time=2.0,
                priority=1,
                tags={"camera", "mode"}
            ),
            Action(
                id="CAM-DET-002_A003",
                description="Verificar controles de zoom estão visíveis",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"video_mode_active"},
                postconditions={"zoom_controls_visible"},
                estimated_time=2.0,
                priority=1,
                tags={"camera", "verification"}
            ),
            Action(
                id="CAM-DET-002_A004",
                description="Aplicar zoom digital de 2x usando gesto de pinça",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"zoom_controls_visible"},
                postconditions={"zoom_2x_applied"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "zoom"}
            ),
            Action(
                id="CAM-DET-002_A005",
                description="Iniciar gravação de vídeo",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"zoom_2x_applied"},
                postconditions={"video_recording_started"},
                estimated_time=2.0,
                priority=1,
                tags={"camera", "recording"}
            ),
            Action(
                id="CAM-DET-002_A006",
                description="Gravar vídeo por 5 segundos com zoom aplicado",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"video_recording_started"},
                postconditions={"video_recorded_with_zoom"},
                estimated_time=5.0,
                priority=1,
                tags={"camera", "recording"}
            ),
            Action(
                id="CAM-DET-002_A007",
                description="Parar gravação e verificar vídeo salvo",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"video_recorded_with_zoom"},
                postconditions={"video_saved"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "verification"}
            ),
        ]
    ))
    
    # Teste: Modo Pro com Ajustes Manuais
    testes.append(TestCase(
        id="CAM-DET-003",
        name="Modo Pro com Ajustes Manuais de ISO e Velocidade",
        description="Captura de foto no modo Pro com ajustes manuais\n\nResultado Esperado: 1- O modo Pro deve estar disponível\n2- Os controles de ISO e velocidade devem estar acessíveis\n3- Os ajustes devem ser aplicados corretamente\n4- A foto deve refletir os ajustes realizados",
        priority=4,
        module="Camera",
        tags={"camera", "pro", "manual", "detailed"},
        validation_point_action="CAM-DET-003_A006",
        actions=[
            Action(
                id="CAM-DET-003_A001",
                description="Abrir aplicativo Câmera",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"camera_app_open"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "navigation"}
            ),
            Action(
                id="CAM-DET-003_A002",
                description="Navegar para modo Pro",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"camera_app_open"},
                postconditions={"pro_mode_active"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "mode"}
            ),
            Action(
                id="CAM-DET-003_A003",
                description="Abrir painel de controles manuais",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"pro_mode_active"},
                postconditions={"manual_controls_panel_open"},
                estimated_time=2.0,
                priority=1,
                tags={"camera", "controls"}
            ),
            Action(
                id="CAM-DET-003_A004",
                description="Ajustar ISO para 400",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"manual_controls_panel_open"},
                postconditions={"iso_set_to_400"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "settings"}
            ),
            Action(
                id="CAM-DET-003_A005",
                description="Ajustar velocidade do obturador para 1/60",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"iso_set_to_400"},
                postconditions={"shutter_speed_set"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "settings"}
            ),
            Action(
                id="CAM-DET-003_A006",
                description="Capturar foto com ajustes manuais aplicados",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"shutter_speed_set"},
                postconditions={"pro_photo_captured"},
                estimated_time=3.0,
                priority=1,
                tags={"camera", "capture"}
            ),
            Action(
                id="CAM-DET-003_A007",
                description="Verificar metadados da foto confirmam ISO e velocidade",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"pro_photo_captured"},
                postconditions={"metadata_verified"},
                estimated_time=4.0,
                priority=1,
                tags={"camera", "verification"}
            ),
        ]
    ))
    
    # ========================================================================
    # CATEGORIA: CONECTIVIDADE - WiFi Detalhado
    # ========================================================================
    
    # Teste: Conectar a WiFi com Senha WPA2
    testes.append(TestCase(
        id="WIFI-DET-001",
        name="Conectar a Rede WiFi com Autenticação WPA2",
        description="Conectar dispositivo a rede WiFi protegida com WPA2\n\nResultado Esperado: 1- As configurações WiFi devem abrir\n2- A lista de redes disponíveis deve ser exibida\n3- A rede selecionada deve solicitar senha\n4- A conexão deve ser estabelecida com sucesso\n5- O dispositivo deve obter IP e conectar à internet",
        priority=5,
        module="Connectivity",
        tags={"wifi", "connectivity", "wpa2", "detailed"},
        validation_point_action="WIFI-DET-001_A005",
        actions=[
            Action(
                id="WIFI-DET-001_A001",
                description="Abrir Configurações do Sistema",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"settings_open"},
                estimated_time=3.0,
                priority=1,
                tags={"settings", "navigation"}
            ),
            Action(
                id="WIFI-DET-001_A002",
                description="Navegar para seção WiFi",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"settings_open"},
                postconditions={"wifi_settings_open"},
                estimated_time=2.0,
                priority=1,
                tags={"wifi", "navigation"}
            ),
            Action(
                id="WIFI-DET-001_A003",
                description="Ativar WiFi se estiver desativado",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"wifi_settings_open"},
                postconditions={"wifi_enabled"},
                estimated_time=2.0,
                priority=1,
                tags={"wifi", "activation"}
            ),
            Action(
                id="WIFI-DET-001_A004",
                description="Verificar lista de redes disponíveis é exibida",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"wifi_enabled"},
                postconditions={"networks_list_visible"},
                estimated_time=3.0,
                priority=1,
                tags={"wifi", "verification"}
            ),
            Action(
                id="WIFI-DET-001_A005",
                description="Selecionar rede WiFi protegida",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"networks_list_visible"},
                postconditions={"network_selected"},
                estimated_time=2.0,
                priority=1,
                tags={"wifi", "selection"}
            ),
            Action(
                id="WIFI-DET-001_A006",
                description="Inserir senha WPA2 no campo de autenticação",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"network_selected"},
                postconditions={"password_entered"},
                estimated_time=5.0,
                priority=1,
                tags={"wifi", "authentication"}
            ),
            Action(
                id="WIFI-DET-001_A007",
                description="Confirmar conexão e aguardar autenticação",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"password_entered"},
                postconditions={"connection_attempt_started"},
                estimated_time=8.0,
                priority=1,
                tags={"wifi", "connection"}
            ),
            Action(
                id="WIFI-DET-001_A008",
                description="Verificar status de conexão mostra 'Conectado'",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"connection_attempt_started"},
                postconditions={"wifi_connected"},
                estimated_time=3.0,
                priority=1,
                tags={"wifi", "verification"}
            ),
            Action(
                id="WIFI-DET-001_A009",
                description="Verificar IP foi atribuído ao dispositivo",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"wifi_connected"},
                postconditions={"ip_assigned"},
                estimated_time=2.0,
                priority=1,
                tags={"wifi", "verification"}
            ),
        ]
    ))
    
    # Teste: Desconectar e Reconectar WiFi
    testes.append(TestCase(
        id="WIFI-DET-002",
        name="Desconectar e Reconectar Automaticamente a WiFi Salva",
        description="Desconectar de WiFi e verificar reconexão automática\n\nResultado Esperado: 1- A WiFi deve ser desconectada\n2- O dispositivo deve tentar reconectar automaticamente\n3- A reconexão deve ocorrer sem solicitar senha novamente\n4- A conexão deve ser restabelecida com sucesso",
        priority=3,
        module="Connectivity",
        tags={"wifi", "reconnection", "detailed"},
        validation_point_action="WIFI-DET-002_A004",
        context_preserving=True,
        actions=[
            Action(
                id="WIFI-DET-002_A001",
                description="Abrir Configurações > WiFi",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"wifi_connected"},
                postconditions={"wifi_settings_open"},
                estimated_time=3.0,
                priority=1,
                tags={"wifi", "navigation"}
            ),
            Action(
                id="WIFI-DET-002_A002",
                description="Verificar rede atual está conectada",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"wifi_settings_open"},
                postconditions={"current_network_verified"},
                estimated_time=2.0,
                priority=1,
                tags={"wifi", "verification"}
            ),
            Action(
                id="WIFI-DET-002_A003",
                description="Desconectar da rede WiFi atual",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"current_network_verified"},
                postconditions={"wifi_disconnected"},
                estimated_time=3.0,
                priority=1,
                tags={"wifi", "disconnect"}
            ),
            Action(
                id="WIFI-DET-002_A004",
                description="Aguardar reconexão automática",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"wifi_disconnected"},
                postconditions={"auto_reconnection_attempted"},
                estimated_time=10.0,
                priority=1,
                tags={"wifi", "verification"}
            ),
            Action(
                id="WIFI-DET-002_A005",
                description="Verificar reconexão ocorreu sem solicitar senha",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"auto_reconnection_attempted"},
                postconditions={"reconnected_without_password"},
                estimated_time=3.0,
                priority=1,
                tags={"wifi", "verification"}
            ),
        ]
    ))
    
    # ========================================================================
    # CATEGORIA: BLUETOOTH - Pareamento Detalhado
    # ========================================================================
    
    # Teste: Parear Dispositivo Bluetooth
    testes.append(TestCase(
        id="BT-DET-001",
        name="Parear Fone de Ouvido Bluetooth",
        description="Parear fone de ouvido Bluetooth com o dispositivo\n\nResultado Esperado: 1- O Bluetooth deve estar ativado\n2- O dispositivo deve estar visível para pareamento\n3- O fone deve aparecer na lista de dispositivos\n4- O pareamento deve ser concluído com sucesso\n5- O fone deve estar disponível para conexão",
        priority=4,
        module="Connectivity",
        tags={"bluetooth", "pairing", "audio", "detailed"},
        validation_point_action="BT-DET-001_A006",
        actions=[
            Action(
                id="BT-DET-001_A001",
                description="Abrir Configurações do Sistema",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"settings_open"},
                estimated_time=3.0,
                priority=1,
                tags={"settings", "navigation"}
            ),
            Action(
                id="BT-DET-001_A002",
                description="Navegar para seção Bluetooth",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"settings_open"},
                postconditions={"bluetooth_settings_open"},
                estimated_time=2.0,
                priority=1,
                tags={"bluetooth", "navigation"}
            ),
            Action(
                id="BT-DET-001_A003",
                description="Ativar Bluetooth se estiver desativado",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"bluetooth_settings_open"},
                postconditions={"bluetooth_enabled"},
                estimated_time=2.0,
                priority=1,
                tags={"bluetooth", "activation"}
            ),
            Action(
                id="BT-DET-001_A004",
                description="Iniciar busca por dispositivos Bluetooth próximos",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"bluetooth_enabled"},
                postconditions={"device_scan_started"},
                estimated_time=5.0,
                priority=1,
                tags={"bluetooth", "scan"}
            ),
            Action(
                id="BT-DET-001_A005",
                description="Verificar fone de ouvido aparece na lista de dispositivos",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"device_scan_started"},
                postconditions={"headphone_found"},
                estimated_time=3.0,
                priority=1,
                tags={"bluetooth", "verification"}
            ),
            Action(
                id="BT-DET-001_A006",
                description="Selecionar fone de ouvido para pareamento",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"headphone_found"},
                postconditions={"pairing_initiated"},
                estimated_time=2.0,
                priority=1,
                tags={"bluetooth", "pairing"}
            ),
            Action(
                id="BT-DET-001_A007",
                description="Confirmar código de pareamento se solicitado",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"pairing_initiated"},
                postconditions={"pairing_code_confirmed"},
                estimated_time=5.0,
                priority=1,
                tags={"bluetooth", "pairing"}
            ),
            Action(
                id="BT-DET-001_A008",
                description="Aguardar conclusão do pareamento",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"pairing_code_confirmed"},
                postconditions={"pairing_completed"},
                estimated_time=8.0,
                priority=1,
                tags={"bluetooth", "verification"}
            ),
            Action(
                id="BT-DET-001_A009",
                description="Verificar fone aparece na lista de dispositivos pareados",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"pairing_completed"},
                postconditions={"headphone_paired"},
                estimated_time=2.0,
                priority=1,
                tags={"bluetooth", "verification"}
            ),
        ]
    ))
    
    # ========================================================================
    # CATEGORIA: BATERIA - Modos de Economia
    # ========================================================================
    
    # Teste: Ativar Modo de Economia de Bateria
    testes.append(TestCase(
        id="BAT-DET-001",
        name="Ativar Modo de Economia de Bateria",
        description="Ativar modo de economia de bateria e verificar efeitos\n\nResultado Esperado: 1- As configurações de bateria devem abrir\n2- O modo de economia deve estar disponível\n3- O modo deve ser ativado com sucesso\n4- As notificações devem indicar modo ativo\n5- O consumo de bateria deve ser reduzido",
        priority=4,
        module="Battery",
        tags={"battery", "power_saving", "detailed"},
        validation_point_action="BAT-DET-001_A004",
        context_preserving=True,
        actions=[
            Action(
                id="BAT-DET-001_A001",
                description="Abrir Configurações do Sistema",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"settings_open"},
                estimated_time=3.0,
                priority=1,
                tags={"settings", "navigation"}
            ),
            Action(
                id="BAT-DET-001_A002",
                description="Navegar para seção Bateria",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"settings_open"},
                postconditions={"battery_settings_open"},
                estimated_time=2.0,
                priority=1,
                tags={"battery", "navigation"}
            ),
            Action(
                id="BAT-DET-001_A003",
                description="Verificar opção Modo de Economia está disponível",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"battery_settings_open"},
                postconditions={"power_saving_option_visible"},
                estimated_time=2.0,
                priority=1,
                tags={"battery", "verification"}
            ),
            Action(
                id="BAT-DET-001_A004",
                description="Ativar Modo de Economia de Bateria",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"power_saving_option_visible"},
                postconditions={"power_saving_enabled"},
                estimated_time=2.0,
                priority=1,
                tags={"battery", "activation"}
            ),
            Action(
                id="BAT-DET-001_A005",
                description="Verificar notificação de modo economia aparece",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"power_saving_enabled"},
                postconditions={"notification_displayed"},
                estimated_time=2.0,
                priority=1,
                tags={"battery", "verification"}
            ),
            Action(
                id="BAT-DET-001_A006",
                description="Verificar indicador de modo economia na barra de status",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"power_saving_enabled"},
                postconditions={"status_indicator_visible"},
                estimated_time=2.0,
                priority=1,
                tags={"battery", "verification"}
            ),
        ]
    ))
    
    # ========================================================================
    # CATEGORIA: SEGURANÇA - Desbloqueio Biométrico
    # ========================================================================
    
    # Teste: Configurar Desbloqueio por Impressão Digital
    testes.append(TestCase(
        id="SEC-DET-001",
        name="Configurar Desbloqueio por Impressão Digital",
        description="Configurar autenticação biométrica por impressão digital\n\nResultado Esperado: 1- As configurações de segurança devem abrir\n2- A opção de impressão digital deve estar disponível\n3- O processo de registro deve iniciar\n4- A impressão deve ser registrada com sucesso\n5- O desbloqueio por impressão deve funcionar",
        priority=5,
        module="Security",
        tags={"security", "biometric", "fingerprint", "detailed"},
        dependencies={"MOTO_SEC_001"},  # Deve vir depois de cadastrar impressão digital
        validation_point_action="SEC-DET-001_A006",
        actions=[
            Action(
                id="SEC-DET-001_A001",
                description="Abrir Configurações do Sistema",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"settings_open"},
                estimated_time=3.0,
                priority=1,
                tags={"settings", "navigation"}
            ),
            Action(
                id="SEC-DET-001_A002",
                description="Navegar para seção Segurança",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"settings_open"},
                postconditions={"security_settings_open"},
                estimated_time=2.0,
                priority=1,
                tags={"security", "navigation"}
            ),
            Action(
                id="SEC-DET-001_A003",
                description="Verificar opção Impressão Digital está disponível",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"security_settings_open"},
                postconditions={"fingerprint_option_visible"},
                estimated_time=2.0,
                priority=1,
                tags={"security", "verification"}
            ),
            Action(
                id="SEC-DET-001_A004",
                description="Inserir PIN ou senha padrão para autenticação",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"fingerprint_option_visible"},
                postconditions={"authentication_completed"},
                estimated_time=5.0,
                priority=1,
                tags={"security", "authentication"}
            ),
            Action(
                id="SEC-DET-001_A005",
                description="Seguir instruções para registrar impressão digital",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"authentication_completed"},
                postconditions={"fingerprint_registration_started"},
                estimated_time=10.0,
                priority=1,
                tags={"security", "registration"}
            ),
            Action(
                id="SEC-DET-001_A006",
                description="Colocar dedo no sensor múltiplas vezes conforme instruções",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"fingerprint_registration_started"},
                postconditions={"fingerprint_registered"},
                estimated_time=15.0,
                priority=1,
                tags={"security", "registration"}
            ),
            Action(
                id="SEC-DET-001_A007",
                description="Verificar mensagem de registro concluído",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"fingerprint_registered"},
                postconditions={"registration_confirmed"},
                estimated_time=2.0,
                priority=1,
                tags={"security", "verification"}
            ),
            Action(
                id="SEC-DET-001_A008",
                description="Bloquear tela e testar desbloqueio com impressão",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"registration_confirmed"},
                postconditions={"fingerprint_unlock_tested"},
                estimated_time=5.0,
                priority=1,
                tags={"security", "verification"}
            ),
        ]
    ))
    
    # ========================================================================
    # CATEGORIA: ÁUDIO - Reprodução e Controles
    # ========================================================================
    
    # Teste: Reproduzir Música com Controles de Mídia
    testes.append(TestCase(
        id="AUD-DET-001",
        name="Reproduzir Música e Testar Controles de Mídia",
        description="Reproduzir música e testar controles de reprodução\n\nResultado Esperado: 1- O aplicativo de música deve abrir\n2- A música deve iniciar reprodução\n3- Os controles devem estar funcionais\n4- As ações de pausar, avançar e voltar devem funcionar\n5- O volume deve ser ajustável",
        priority=3,
        module="Audio",
        tags={"audio", "music", "playback", "detailed"},
        validation_point_action="AUD-DET-001_A004",
        context_preserving=True,
        actions=[
            Action(
                id="AUD-DET-001_A001",
                description="Abrir aplicativo de Música",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"music_app_open"},
                estimated_time=3.0,
                priority=1,
                tags={"audio", "navigation"}
            ),
            Action(
                id="AUD-DET-001_A002",
                description="Navegar para biblioteca de músicas",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"music_app_open"},
                postconditions={"music_library_open"},
                estimated_time=2.0,
                priority=1,
                tags={"audio", "navigation"}
            ),
            Action(
                id="AUD-DET-001_A003",
                description="Selecionar uma música da biblioteca",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"music_library_open"},
                postconditions={"song_selected"},
                estimated_time=2.0,
                priority=1,
                tags={"audio", "selection"}
            ),
            Action(
                id="AUD-DET-001_A004",
                description="Iniciar reprodução da música",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"song_selected"},
                postconditions={"playback_started"},
                estimated_time=2.0,
                priority=1,
                tags={"audio", "playback"}
            ),
            Action(
                id="AUD-DET-001_A005",
                description="Verificar música está reproduzindo e controles visíveis",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"playback_started"},
                postconditions={"playback_verified"},
                estimated_time=3.0,
                priority=1,
                tags={"audio", "verification"}
            ),
            Action(
                id="AUD-DET-001_A006",
                description="Pausar reprodução usando botão de pausa",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"playback_verified"},
                postconditions={"playback_paused"},
                estimated_time=2.0,
                priority=1,
                tags={"audio", "controls"}
            ),
            Action(
                id="AUD-DET-001_A007",
                description="Retomar reprodução usando botão de play",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"playback_paused"},
                postconditions={"playback_resumed"},
                estimated_time=2.0,
                priority=1,
                tags={"audio", "controls"}
            ),
            Action(
                id="AUD-DET-001_A008",
                description="Avançar para próxima música",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"playback_resumed"},
                postconditions={"next_song_playing"},
                estimated_time=2.0,
                priority=1,
                tags={"audio", "controls"}
            ),
            Action(
                id="AUD-DET-001_A009",
                description="Voltar para música anterior",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"next_song_playing"},
                postconditions={"previous_song_playing"},
                estimated_time=2.0,
                priority=1,
                tags={"audio", "controls"}
            ),
            Action(
                id="AUD-DET-001_A010",
                description="Ajustar volume usando controles de hardware",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"previous_song_playing"},
                postconditions={"volume_adjusted"},
                estimated_time=2.0,
                priority=1,
                tags={"audio", "controls"}
            ),
        ]
    ))
    
    # ========================================================================
    # CATEGORIA: MENSAGENS SMS - Envio e Recebimento
    # ========================================================================
    
    # Teste: Enviar SMS para Contato
    testes.append(TestCase(
        id="SMS-DET-001",
        name="Enviar Mensagem SMS para Contato",
        description="Enviar mensagem SMS para um contato existente\n\nResultado Esperado: 1- O aplicativo de Mensagens deve abrir\n2- A opção de nova mensagem deve estar disponível\n3- O contato deve ser selecionável\n4- A mensagem deve ser digitada e enviada\n5- A mensagem deve aparecer na conversa como enviada",
        priority=4,
        module="SMS",
        tags={"sms", "messaging", "detailed"},
        validation_point_action="SMS-DET-001_A005",
        actions=[
            Action(
                id="SMS-DET-001_A001",
                description="Abrir aplicativo de Mensagens",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"sim_card_inserted"},
                postconditions={"messages_app_open"},
                estimated_time=3.0,
                priority=1,
                tags={"sms", "navigation"}
            ),
            Action(
                id="SMS-DET-001_A002",
                description="Verificar lista de conversas é exibida",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"messages_app_open"},
                postconditions={"conversations_list_visible"},
                estimated_time=2.0,
                priority=1,
                tags={"sms", "verification"}
            ),
            Action(
                id="SMS-DET-001_A003",
                description="Tocar no botão de nova mensagem",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"conversations_list_visible"},
                postconditions={"new_message_screen_open"},
                estimated_time=2.0,
                priority=1,
                tags={"sms", "navigation"}
            ),
            Action(
                id="SMS-DET-001_A004",
                description="Selecionar contato do destinatário",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"new_message_screen_open"},
                postconditions={"recipient_selected"},
                estimated_time=4.0,
                priority=1,
                tags={"sms", "selection"}
            ),
            Action(
                id="SMS-DET-001_A005",
                description="Digitar mensagem de teste no campo de texto",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"recipient_selected"},
                postconditions={"message_text_entered"},
                estimated_time=5.0,
                priority=1,
                tags={"sms", "input"}
            ),
            Action(
                id="SMS-DET-001_A006",
                description="Enviar mensagem usando botão de envio",
                action_type=ActionType.CREATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"message_text_entered"},
                postconditions={"message_sent"},
                estimated_time=3.0,
                priority=1,
                tags={"sms", "send"}
            ),
            Action(
                id="SMS-DET-001_A007",
                description="Verificar mensagem aparece na conversa como enviada",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"message_sent"},
                postconditions={"message_displayed_as_sent"},
                estimated_time=3.0,
                priority=1,
                tags={"sms", "verification"}
            ),
            Action(
                id="SMS-DET-001_A008",
                description="Verificar indicador de status de entrega",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"message_displayed_as_sent"},
                postconditions={"delivery_status_verified"},
                estimated_time=2.0,
                priority=1,
                tags={"sms", "verification"}
            ),
        ]
    ))
    
    # ========================================================================
    # CATEGORIA: TELA/DISPLAY - Brilho e Cores
    # ========================================================================
    
    # Teste: Ajustar Brilho da Tela
    testes.append(TestCase(
        id="DISP-DET-001",
        name="Ajustar Brilho da Tela Manualmente",
        description="Ajustar brilho da tela usando controles manuais\n\nResultado Esperado: 1- As configurações de display devem abrir\n2- O controle de brilho deve estar acessível\n3- O brilho deve ser ajustável\n4- As alterações devem ser aplicadas imediatamente\n5- O brilho deve ser mantido após ajuste",
        priority=3,
        module="Display",
        tags={"display", "brightness", "detailed"},
        validation_point_action="DISP-DET-001_A004",
        context_preserving=True,
        teardown_restores=True,
        actions=[
            Action(
                id="DISP-DET-001_A001",
                description="Abrir Configurações do Sistema",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions=set(),
                postconditions={"settings_open"},
                estimated_time=3.0,
                priority=1,
                tags={"settings", "navigation"}
            ),
            Action(
                id="DISP-DET-001_A002",
                description="Navegar para seção Display",
                action_type=ActionType.NAVIGATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"settings_open"},
                postconditions={"display_settings_open"},
                estimated_time=2.0,
                priority=1,
                tags={"display", "navigation"}
            ),
            Action(
                id="DISP-DET-001_A003",
                description="Localizar controle de Brilho",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"display_settings_open"},
                postconditions={"brightness_control_visible"},
                estimated_time=2.0,
                priority=1,
                tags={"display", "verification"}
            ),
            Action(
                id="DISP-DET-001_A004",
                description="Ajustar brilho para 50% usando slider",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"brightness_control_visible"},
                postconditions={"brightness_set_to_50"},
                estimated_time=3.0,
                priority=1,
                tags={"display", "adjustment"}
            ),
            Action(
                id="DISP-DET-001_A005",
                description="Verificar brilho da tela mudou imediatamente",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"brightness_set_to_50"},
                postconditions={"brightness_change_verified"},
                estimated_time=2.0,
                priority=1,
                tags={"display", "verification"}
            ),
            Action(
                id="DISP-DET-001_A006",
                description="Ajustar brilho para máximo (100%)",
                action_type=ActionType.MODIFICATION,
                impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                preconditions={"brightness_change_verified"},
                postconditions={"brightness_set_to_max"},
                estimated_time=2.0,
                priority=1,
                tags={"display", "adjustment"}
            ),
            Action(
                id="DISP-DET-001_A007",
                description="Verificar brilho máximo foi aplicado",
                action_type=ActionType.VERIFICATION,
                impact=ActionImpact.NON_DESTRUCTIVE,
                preconditions={"brightness_set_to_max"},
                postconditions={"max_brightness_verified"},
                estimated_time=2.0,
                priority=1,
                tags={"display", "verification"}
            ),
        ]
    ))
    
    return testes
